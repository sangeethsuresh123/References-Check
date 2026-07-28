import re
import json
import sys
import io
import os
import time
import requests
import feedparser
import xml.etree.ElementTree as ET
from urllib.parse import quote
from pypdf import PdfReader
from habanero import Crossref
from fuzzywuzzy import fuzz
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WITH_DOI = r'^(.+?)\.\s*(\d{4})\.\s*(.+?)\s*(?:https?://)?(?:doi\.org[:/]?|doi:?\s*)([\d\.\/\w\-]+)'
WITHOUT_DOI = r'^(.+?)\.\s*(\d{4})\.\s*(.+?)\.?$'

cr = Crossref()
ARXIV_URL = "http://export.arxiv.org/api/query"
OPENALEX_URL = "https://api.openalex.org/works?api_key=ISdnwS4MjMUpX9XkOYChZt"
DBLP_URL = "https://dblp.org/search/publ/api"
S2_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
PUBMED_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
EUROPE_PMC_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
OPENLIBRARY_URL = "https://openlibrary.org/search.json"
GOVINFO_URL = "https://api.govinfo.gov/search"
SEARXNG_URL = "https://search.sapti.me/search"

llm_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)
LLM_MODEL = "qwen/qwen-2.5-7b-instruct"


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------

def extract_references(filename):
    reader = PdfReader(filename)
    req_content = ""
    flag = 0
    for pgno in range(len(reader.pages)):
        page = reader.pages[pgno]
        content = page.extract_text()
        if flag == 1:
            req_content += content
        if "REFERENCES" in content or "References" in content:
            split_content = re.split(r'(?i)references', content)
            req_content += split_content[-1]
            flag = 1
    req_content = req_content.strip().replace("\n", " ")
    ref_list = re.split(r'\[\d+\]', req_content)
    ref_list = [entry.strip() for entry in ref_list]
    ref_list = ref_list[1:]
    return ref_list


def clean_reference(text):
    text = re.sub(r'\.([A-Z])', r'. \1', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\n', ' ').replace('\r', ' ')
    return text.strip()


def check_authors(api_authors, ref_authors):
    for api_author in api_authors:
        matched = False
        for ref_author in ref_authors:
            if fuzz.ratio(api_author, ref_author) > 80:
                matched = True
                break
        if not matched:
            return True
    return False


def title_mismatch(api_title, query):
    if not api_title or not query:
        return False
    return fuzz.ratio(api_title.lower(), query.lower()) <= 80


def doi_mismatch(ref_doi, api_doi):
    if not ref_doi or not api_doi:
        return False
    return ref_doi.strip() != api_doi.strip()


def make_result(source, title, authors, doi, suspect):
    return {
        "source": source,
        "title": title or "",
        "authors": authors or [],
        "doi": doi,
        "suspect": suspect,
    }


def llm_extract_fields(reference_text):
    prompt = f"""Extract the following fields from this academic reference and return ONLY a JSON object with no other text:

Reference: {reference_text}

Return JSON with these keys:
- "authors": list of author full names
- "title": the paper/book title as a string
- "year": publication year as a string
- "doi": the DOI if present, otherwise null
- "venue": the conference/journal name if present, otherwise null
- "type": one of "journal", "conference", "preprint", "book", "webpage", "patent", "other"

Return ONLY the JSON object, no explanation."""

    try:
        response = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = re.sub(r'^```(?:json)?\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
        return json.loads(content)
    except Exception as e:
        print(f"    LLM extraction failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Source 1: DOI Resolver  (validate by resolving DOI via doi.org)
# ---------------------------------------------------------------------------

def try_doi_resolver(query, ref_authors, ref_doi=None):
    if not ref_doi:
        return None, "no DOI to resolve"
    try:
        resp = requests.get(
            f"https://doi.org/{ref_doi}",
            headers={"Accept": "application/vnd.citationstyle.csl+json"},
            timeout=10,
        )
        if resp.status_code != 200:
            return None, f"HTTP {resp.status_code}"
        data = resp.json()
        title = data.get("title", "")
        api_authors = []
        for author in data.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            api_authors.append(f"{given} {family}".strip())
        suspect = title_mismatch(title, query) or check_authors(api_authors, ref_authors)
        return make_result("DOI Resolver", title, api_authors, ref_doi, suspect), None
    except Exception as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# Source 2: CrossRef
# ---------------------------------------------------------------------------

def try_crossref(query, ref_authors, ref_doi=None):
    try:
        search_result = cr.works(query=query, limit=1)
        items = search_result['message']['items']
        if not items:
            return None, "no results"
        item = items[0]
        title = item.get('title', [''])[0]
        api_authors = []
        for author in item.get('author', []):
            given = author.get('given', '')
            family = author.get('family', '')
            api_authors.append(f"{given} {family}".strip())
        api_doi = item.get('DOI', None)
        suspect = check_authors(api_authors, ref_authors) or doi_mismatch(ref_doi, api_doi)
        return make_result("Crossref", title, api_authors, api_doi, suspect), None
    except Exception as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# Source 3: Semantic Scholar
# ---------------------------------------------------------------------------

def try_semantic_scholar(query, ref_authors, ref_doi=None):
    try:
        params = {
            "query": query,
            "fields": "title,authors,externalIds,year,venue",
            "limit": 1,
        }
        resp = requests.get(S2_URL, params=params, timeout=10)
        data = resp.json()
        papers = data.get("data", [])
        if not papers:
            return None, "no results"
        paper = papers[0]
        title = paper.get("title", "")
        api_authors = [a.get("name", "") for a in paper.get("authors", [])]
        ext_ids = paper.get("externalIds", {}) or {}
        api_doi = ext_ids.get("DOI", None)
        suspect = check_authors(api_authors, ref_authors) or doi_mismatch(ref_doi, api_doi)
        return make_result("Semantic Scholar", title, api_authors, api_doi, suspect), None
    except Exception as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# Source 4: DBLP
# ---------------------------------------------------------------------------

def try_dblp(query, ref_authors, ref_doi=None):
    try:
        params = {"q": query, "format": "json", "h": 1}
        resp = requests.get(DBLP_URL, params=params, timeout=10)
        data = resp.json()
        hits = data.get("result", {}).get("hits", {}).get("hit", [])
        if not hits:
            return None, "no results"
        info = hits[0].get("info", {})
        title = info.get("title", "")
        authors_data = info.get("authors", {}).get("author", [])
        if isinstance(authors_data, dict):
            authors_data = [authors_data]
        api_authors = [a.get("text", "") for a in authors_data]
        api_doi = info.get("doi", None)
        suspect = check_authors(api_authors, ref_authors) or doi_mismatch(ref_doi, api_doi)
        return make_result("DBLP", title, api_authors, api_doi, suspect), None
    except Exception as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# Source 5: arXiv
# ---------------------------------------------------------------------------

def try_arxiv(query, ref_authors, ref_doi=None):
    try:
        search_url = f"{ARXIV_URL}?search_query=all:{query.replace(' ', '+')}&start=0&max_results=1"
        feed = feedparser.parse(search_url)
        if not feed.entries:
            return None, "no results"
        paper = feed.entries[0]
        title = paper.title
        api_authors = [a.name for a in paper.authors]
        api_doi = getattr(paper, "arxiv_doi", None)
        suspect = title_mismatch(title, query) or check_authors(api_authors, ref_authors) or doi_mismatch(ref_doi, api_doi)
        return make_result("arXiv", title, api_authors, api_doi, suspect), None
    except Exception as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# Source 6: OpenAlex
# ---------------------------------------------------------------------------

def try_openalex(query, ref_authors, ref_doi=None):
    try:
        params = {"search": query}
        resp = requests.get(OPENALEX_URL, params=params, timeout=10)
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return None, "no results"
        work = results[0]
        title = work.get("title", "")
        api_authors = [
            a.get("author", {}).get("display_name", "")
            for a in work.get("authorships", [])
        ]
        api_doi = work.get("doi", None)
        suspect = check_authors(api_authors, ref_authors) or doi_mismatch(ref_doi, api_doi)
        return make_result("OpenAlex", title, api_authors, api_doi, suspect), None
    except Exception as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# Source 7: PubMed
# ---------------------------------------------------------------------------

def try_pubmed(query, ref_authors, ref_doi=None):
    try:
        search_resp = requests.get(PUBMED_SEARCH, params={
            "db": "pubmed", "term": query, "retmode": "json", "retmax": 1
        }, timeout=10)
        ids = search_resp.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return None, "no results"
        fetch_resp = requests.get(PUBMED_FETCH, params={
            "db": "pubmed", "id": ids[0], "retmode": "xml", "rettype": "abstract"
        }, timeout=10)
        root = ET.fromstring(fetch_resp.text)
        article = root.find(".//PubmedArticle/MedlineCitation/Article")
        if article is None:
            return None, "parse error"
        title_el = article.find("ArticleTitle")
        title = title_el.text if title_el is not None else ""
        api_authors = []
        for author in article.findall(".//AuthorList/Author"):
            last = author.findtext("LastName", "")
            fore = author.findtext("ForeName", "")
            api_authors.append(f"{fore} {last}".strip())
        api_doi = None
        for aid in root.findall(".//PubmedData/ArticleIdList/ArticleId"):
            if aid.get("IdType") == "doi":
                api_doi = aid.text
                break
        suspect = check_authors(api_authors, ref_authors) or doi_mismatch(ref_doi, api_doi)
        return make_result("PubMed", title, api_authors, api_doi, suspect), None
    except Exception as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# Source 8: Europe PMC
# ---------------------------------------------------------------------------

def try_europepmc(query, ref_authors, ref_doi=None):
    try:
        params = {"query": query, "format": "json", "resultType": "core", "pageSize": 1}
        resp = requests.get(EUROPE_PMC_URL, params=params, timeout=10)
        data = resp.json()
        results = data.get("resultList", {}).get("result", [])
        if not results:
            return None, "no results"
        work = results[0]
        title = work.get("title", "")
        author_str = work.get("authorString", "")
        api_authors = [a.strip() for a in author_str.split(",")] if author_str else []
        api_doi = work.get("doi", None)
        suspect = check_authors(api_authors, ref_authors) or doi_mismatch(ref_doi, api_doi)
        return make_result("Europe PMC", title, api_authors, api_doi, suspect), None
    except Exception as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# Source 9: ACL Anthology (web scrape fallback — no search API)
# ---------------------------------------------------------------------------

def try_acl_anthology(query, ref_authors, ref_doi=None):
    try:
        resp = requests.get(
            "https://aclanthology.org/search/",
            params={"q": query},
            headers={"User-Agent": "RefCheck/1.0"},
            timeout=10,
        )
        if resp.status_code != 200:
            return None, f"HTTP {resp.status_code}"
        text = resp.text
        title_match = re.search(r'<span class="d-block">(.+?)</span>', text)
        if not title_match:
            return None, "no parseable result"
        title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
        api_authors = []
        for m in re.finditer(r'class="align-middle"[^>]*>([^<]+)</a>', text):
            api_authors.append(m.group(1).strip())
        api_doi = ref_doi
        suspect = title_mismatch(title, query) or check_authors(api_authors, ref_authors)
        return make_result("ACL Anthology", title, api_authors, api_doi, suspect), None
    except Exception as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# Source 10: Open Library (books, technical reports)
# ---------------------------------------------------------------------------

def try_openlibrary(query, ref_authors, ref_doi=None):
    try:
        params = {"q": query, "limit": 1}
        resp = requests.get(OPENLIBRARY_URL, params=params, timeout=10)
        data = resp.json()
        docs = data.get("docs", [])
        if not docs:
            return None, "no results"
        work = docs[0]
        title = work.get("title", "")
        api_authors = work.get("author_name", [])
        suspect = title_mismatch(title, query) or check_authors(api_authors, ref_authors)
        return make_result("Open Library", title, api_authors, ref_doi, suspect), None
    except Exception as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# Source 11: GovInfo (US federal documents)
# ---------------------------------------------------------------------------

def try_govinfo(query, ref_authors, ref_doi=None):
    try:
        params = {"query": query, "pageSize": 1, "api_key": "DEMO_KEY"}
        resp = requests.get(GOVINFO_URL, params=params, timeout=10)
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return None, "no results"
        work = results[0]
        title = work.get("title", "")
        suspect = title_mismatch(title, query)
        return make_result("GovInfo", title, [], ref_doi, suspect), None
    except Exception as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# Source 12: IACR ePrint (cryptology — OAI-PMH scrape)
# ---------------------------------------------------------------------------

def try_iacr(query, ref_authors, ref_doi=None):
    try:
        resp = requests.get(
            "https://eprint.iacr.org/search",
            params={"q": query},
            headers={"User-Agent": "RefCheck/1.0"},
            timeout=10,
        )
        if resp.status_code != 200:
            return None, f"HTTP {resp.status_code}"
        text = resp.text
        title_match = re.search(r'<dt>.*?<a[^>]*>([^<]+)</a>', text)
        if not title_match:
            return None, "no parseable result"
        title = title_match.group(1).strip()
        api_doi = ref_doi
        suspect = title_mismatch(title, query)
        return make_result("IACR ePrint", title, [], api_doi, suspect), None
    except Exception as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# Source 13: URL Checker (liveness check for non-academic URLs)
# ---------------------------------------------------------------------------

def try_url_checker(query, ref_authors, ref_doi=None):
    url_match = re.search(r'https?://[^\s]+', query)
    if not url_match:
        url = query
    else:
        url = url_match.group(0)
    try:
        resp = requests.head(url, timeout=10, allow_redirects=True)
        suspect = resp.status_code >= 400
        return make_result("URL Checker", query, [], None, suspect), None
    except Exception as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# Source 14: SearxNG Web Search (ultimate fallback)
# ---------------------------------------------------------------------------

def try_searxng(query, ref_authors, ref_doi=None):
    try:
        params = {"q": query, "format": "json", "categories": "science"}
        resp = requests.get(SEARXNG_URL, params=params, timeout=10)
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return None, "no results"
        first = results[0]
        title = first.get("title", "")
        suspect = title_mismatch(title, query)
        return make_result("SearxNG", title, [], ref_doi, suspect), None
    except Exception as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# Master verification — try sources in priority order with fallback
# ---------------------------------------------------------------------------

SOURCE_CHAIN = [
    ("DOI Resolver",  try_doi_resolver),
    ("Crossref",      try_crossref),
    ("Semantic Scholar", try_semantic_scholar),
    ("DBLP",          try_dblp),
    ("arXiv",         try_arxiv),
    ("OpenAlex",      try_openalex),
    ("PubMed",        try_pubmed),
    ("Europe PMC",    try_europepmc),
    ("ACL Anthology", try_acl_anthology),
    ("Open Library",  try_openlibrary),
    ("GovInfo",       try_govinfo),
    ("IACR ePrint",   try_iacr),
    ("URL Checker",   try_url_checker),
    ("SearxNG",       try_searxng),
]


def verify_reference(query, ref_authors, ref_doi=None):
    for name, func in SOURCE_CHAIN:
        result, error = func(query, ref_authors, ref_doi)
        if result:
            return result
    return make_result("None", "", [], None, True)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parser(filepath):
    ref_list = extract_references(filepath)
    final_list = []
    count = 0
    suspect = 0
    llm_failed = 0

    for entry in ref_list:
        count += 1
        ref_entry = {}
        entry = clean_reference(entry)
        print(f"[{count}] {entry[:70]}...")

        print("  Extracting fields via LLM...")
        fields = llm_extract_fields(entry)
        if not fields:
            llm_failed += 1
            print("  LLM extraction failed, skipping")
            ref_entry["id"] = count
            ref_entry["raw"] = entry
            ref_entry["llm_extracted"] = None
            ref_entry["verified"] = make_result("None", "", [], None, True)
            final_list.append(ref_entry)
            print()
            continue

        ref_entry["id"] = count
        ref_entry["raw"] = entry
        ref_entry["llm_extracted"] = fields

        title = fields.get("title", "")
        authors = fields.get("authors", [])
        doi = fields.get("doi", None)

        print(f"  Title:   {title}")
        print(f"  Authors: {authors}")
        print(f"  DOI:     {doi}")

        result = verify_reference(title, authors, doi)
        ref_entry["verified"] = result
        if result["suspect"]:
            suspect += 1
            print(f"  -> SUSPECT (via {result['source']})")
        else:
            print(f"  -> OK (via {result['source']})")
        print()

    print("=" * 50)
    print("Total:    ", count)
    print("Suspect:  ", suspect)
    print("LLM fails:", llm_failed)
    return final_list


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python full_reference_checker.py <path_to_pdf>")
        sys.exit(1)
    pdf_path = sys.argv[1]
    output = parser(pdf_path)
