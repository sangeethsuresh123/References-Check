import re
import json
import os
import time
import requests
import feedparser
from pypdf import PdfReader
from habanero import Crossref
from fuzzywuzzy import fuzz
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

WITH_DOI = r'^(.+?)\.\s*(\d{4})\.\s*(.+?)\s*(?:https?://)?(?:doi\.org[:/]?|doi:?\s*)([\d\.\/\w\-]+)'
WITHOUT_DOI = r'^(.+?)\.\s*(\d{4})\.\s*(.+?)\.?$'

cr = Crossref()
ARXIV_URL = "http://export.arxiv.org/api/query"
OPENALEX_URL = "https://api.openalex.org/works?api_key=ISdnwS4MjMUpX9XkOYChZt"

llm_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)
LLM_MODEL = "qwen/qwen-2.5-7b-instruct"


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


def verify_reference(query, ref_authors, ref_doi=None):
    for name, func in [("Crossref", try_crossref), ("arXiv", try_arxiv), ("OpenAlex", try_openalex)]:
        result, error = func(query, ref_authors, ref_doi)
        if result:
            return result
    return make_result("None", "", [], None, True)


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

        print(f"  Title:  {title}")
        print(f"  Authors: {authors}")
        print(f"  DOI:    {doi}")

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
        print("Usage: python llm_based_reference_checker.py <path_to_pdf>")
        sys.exit(1)
    pdf_path = sys.argv[1]
    output = parser(pdf_path)
