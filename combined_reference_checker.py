import re
import time
import requests
import feedparser
from pypdf import PdfReader
from habanero import Crossref
from fuzzywuzzy import fuzz

WITH_DOI = r'^(.+?)\.\s*(\d{4})\.\s*(.+?)\s*(?:https?://)?(?:doi\.org[:/]?|doi:?\s*)([\d\.\/\w\-]+)'
WITHOUT_DOI = r'^(.+?)\.\s*(\d{4})\.\s*(.+?)\.?$'

cr = Crossref()
ARXIV_URL = "http://export.arxiv.org/api/query"
OPENALEX_URL = "https://api.openalex.org/works?api_key=ISdnwS4MjMUpX9XkOYChZt"


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


def extract_authors(authors):
    if "," in authors:
        author_list = authors.split(",")
        author_list[-1] = author_list[-1].split("and")[-1]
    else:
        author_list = authors.split(" and ")
    for i in range(len(author_list)):
        author_list[i] = author_list[i].strip().replace("\n", " ")
    return author_list


def clean_reference(text):
    text = re.sub(r'\.([A-Z])', r'. \1', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\n', ' ').replace('\r', ' ')
    return text.strip()


def clean_reference_2(text):
    text = re.sub(r'\.([A-Z])', r'. \1', text)
    text = re.sub(r'\s+', '', text)
    text = text.replace('\n', '').replace('\r', '')
    return text.strip()


def check_authors(api_authors, ref_authors):
    for api_author in api_authors:
        flag = True
        for ref_author in ref_authors:
            if fuzz.ratio(api_author, ref_author) > 80:
                flag = False
                break
        if not flag:
            return False
    return True


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
        author_mismatch = check_authors(api_authors, ref_authors)
        doi_mismatch = ref_doi and api_doi and api_doi != ref_doi
        return {
            "source": "Crossref",
            "title": title,
            "authors": api_authors,
            "doi": api_doi,
            "suspect": author_mismatch or doi_mismatch
        }, None
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
        title_mismatch = fuzz.ratio(title, query) <= 80
        author_mismatch = check_authors(api_authors, ref_authors)
        doi_mismatch = ref_doi and api_doi and api_doi != ref_doi
        return {
            "source": "arXiv",
            "title": title,
            "authors": api_authors,
            "doi": api_doi,
            "suspect": title_mismatch or author_mismatch or doi_mismatch
        }, None
    except Exception as e:
        return None, str(e)


def try_openalex(query, ref_authors, ref_doi=None):
    try:
        params = {"search": query}
        response = requests.get(OPENALEX_URL, params=params)
        data = response.json()
        results = data.get("results", [])
        if not results:
            return None, "no results"
        work = results[0]
        title = work.get("title", "")
        api_authors = [
            author.get("author", {}).get("display_name")
            for author in work.get("authorships", [])
        ]
        api_doi = work.get("doi", None)
        title_mismatch = fuzz.ratio(title, query) <= 80
        author_mismatch = check_authors(api_authors, ref_authors)
        doi_mismatch = ref_doi and api_doi and api_doi != ref_doi
        return {
            "source": "OpenAlex",
            "title": title,
            "authors": api_authors,
            "doi": api_doi,
            "suspect": title_mismatch or author_mismatch or doi_mismatch
        }, None
    except Exception as e:
        return None, str(e)


def verify_reference(query, ref_authors, ref_doi=None):
    result, error = try_crossref(query, ref_authors, ref_doi)
    if result:
        return result
    print(f"  Crossref failed ({error}), trying arXiv...")
    time.sleep(3)
    result, error = try_arxiv(query, ref_authors, ref_doi)
    if result:
        return result
    print(f"  arXiv failed ({error}), trying OpenAlex...")
    result, error = try_openalex(query, ref_authors, ref_doi)
    if result:
        return result
    print(f"  OpenAlex failed ({error}), all sources exhausted")
    return {"source": "None", "title": "", "authors": [], "doi": None, "suspect": True}


def parser(filepath):
    ref_list = extract_references(filepath)
    final_list = []
    count = 0
    matched = 0
    suspect = 0
    for entry in ref_list:
        count += 1
        ref_entry = {}
        entry = clean_reference(entry)
        match_check = re.match(WITH_DOI, entry)
        if match_check:
            matched += 1
            ref_entry["id"] = count
            ref_entry["authors"] = extract_authors(match_check.group(1))
            ref_entry["year"] = match_check.group(2)
            ref_entry["x"] = match_check.group(3)
            entry_clean = clean_reference_2(entry)
            match_clean = re.match(WITH_DOI, entry_clean)
            if match_clean:
                ref_entry["doi"] = match_clean.group(4)
            else:
                ref_entry["doi"] = match_check.group(4)
            print(f"[{count}] {ref_entry['x'][:60]}...")
            result = verify_reference(ref_entry["x"], ref_entry["authors"], ref_entry["doi"])
            ref_entry["verified"] = result
            if result["suspect"]:
                suspect += 1
                print(f"  -> SUSPECT (via {result['source']})")
            else:
                print(f"  -> OK (via {result['source']})")
        elif re.match(WITHOUT_DOI, entry):
            matched += 1
            match_check = re.match(WITHOUT_DOI, entry)
            ref_entry["id"] = count
            ref_entry["authors"] = extract_authors(match_check.group(1))
            ref_entry["year"] = match_check.group(2)
            ref_entry["x"] = match_check.group(3)
            print(f"[{count}] {ref_entry['x'][:60]}...")
            result = verify_reference(ref_entry["x"], ref_entry["authors"])
            ref_entry["verified"] = result
            if result["suspect"]:
                suspect += 1
                print(f"  -> SUSPECT (via {result['source']})")
            else:
                print(f"  -> OK (via {result['source']})")
        final_list.append(ref_entry)
        print()
    print("=" * 50)
    print("Matched: ", matched)
    print("Total: ", count)
    print("Suspect: ", suspect)
    return final_list


output = parser("testfile.pdf")
