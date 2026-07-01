import re
from pypdf import PdfReader

# Helper function to clean references


def clean_reference(text):
    """Clean common issues in PDF-extracted references"""
    # Add space between period and capital letter (fixes "Treatment.Journal")
    text = re.sub(r'\.([A-Z])', r'. \1', text)
    # Normalize multiple spaces to single space
    text = re.sub(r'\s+', ' ', text)
    # Remove line breaks
    text = text.replace('\n', ' ').replace('\r', ' ')
    # Trim whitespace
    return text.strip()


# UPDATED REGEX PATTERNS - with flexible spacing and en-dash support
pag_article_journal_1 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(.+?)\s+(\d+),\s+(\d+)\s+\((?:[A-Za-z]+\.?\s+)?\d{4}\),\s+(\d+)[–\-](\d+)\.?\s*(?:https?://doi\.org/([\d\.\/]+))?$'

enum_article_journal_2 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(.+?)\s+(\d+),\s+(\d+),\s+Article\s+(\d+)\s+\((?:[A-Za-z]+\.?\s+)?\d{4}\),\s+(\d+)\s+pages?\.?\s*(?:https?://doi\.org/([\d\.\/]+))?$'

monograph_book_3 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\s+\((\d+(?:st|nd|rd|th))\.?\s+ed\.?\)\.\s+(.+?),\s+(.+?)(?:,\s+([A-Z]{2}))?\.?$'

divisible_book_4 = r'^(.+?)\s+\(Eds?\.?\)\.\s+(\d{4})\.\s+(.+?)\s+\((\d+(?:st|nd|rd|th))\.?\s+ed\.?\)\.\s+(.+?),\s+Vol\.?\s+(\d+)\.\s+(.+?),\s+(.+?)\.?\s*(?:https?://doi\.org/([\d\.\/\-]+))?$'

multi_vol_work_5 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?),\s+Vol\.?\s+(\d+):\s+(.+?)\s+\((\d+(?:st|nd|rd|th))\.?\s+ed\.?\)\.\s+(.+?)\.?$'

chap_edited_not_series_6 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+In\s+(.+?)\.\s+(.+?)\s+\(Eds?\.?\),\s+(.+?),\s+(\d+)[–\-](\d+)\.?$'

article_conference_7 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+In\s+(?:Proceedings of the\s+)?(.+?)\s+\(([A-Z]+\s*\'?\d{2})\),\s+([A-Za-z]+\s+\d{1,2}\s*[–\-]\s*\d{1,2},\s+\d{4}),\s+(.+?)\.\s+(.+?),\s+(.+?),\s+([A-Z]{2}),\s+(\d+)[–\-](\d+)\.?\s*(?:https?://doi\.org/([\d\.\/]+))?$'

patent_8 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+\(([A-Za-z]+\.?\s+\d{4})\)\.\s+Patent No\.?\s+(\d+),\s+Filed\s+(.+?),\s+Issued\s+(.+?)\.?$'

technical_report_9 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(.+?)\s+(Technical Report|TR)\s+([A-Z]+-?\d+)\.\s+(.+?),\s+(.+?)(?:,\s+([A-Z]{2}))?\.?$'

doctoral_dissertation_10 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\s+\((.+?)\)\.\s+(Ph\.?D\.?|Master\'?s)\s+Dissertation\.\s+(.+?),\s+(.+?),\s+([A-Z]{2})\.\s+UMI Order Number:\s+([A-Z]+\s+\d+)\.?$'

masters_thesis_11 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(Master\'?s\s+thesis|Ph\.?D\.?\s+Dissertation)\.\s+(.+?),\s+(.+?),\s+(.+?)\.?$'

www_link_12 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+\(([A-Za-z]+\.?\s+\d{4})\)\.\s+Retrieved\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})\s+from\s+(https?://[^\s,]+),?\s*archived at\s+\[?(https?://[^\]\s]+)\]?\.?$'

www_link_13 = r'^(.+?)\.\s+(.+?)\.\s+Retrieved from\s+(https?://\S+?)\.?$'

www_link_14 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+Retrieved from\s+(https?://\S+?)\.?$'

video_link_15 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+Video\.\s+In\s+(.+?)\s+\(([A-Za-z]+\s+\d{1,2}[–\-]\d{1,2},\s+\d{4})\)\.\s+(.+?),\s+(.+?),\s+([A-Z]{2}),\s+(\d+)\.?\s*(?:https?://doi\.org/([\d\.\/\w\-]+))?$'

video_link_16 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+Video\.\s+\((\d{1,2}\s+[A-Za-z]+\s+\d{4})\)\.\s+Retrieved\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})\s+from\s+(https?://[^\s,]+),?\s*archived at\s+\[?(https?://[^\]\s]+)\]?\.?$'

arxiv_17 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s*arXiv\s*(?:preprint\s+)?arXiv:([\d\.]+)(?:\s+\(\d{4}\))?\.?\s*(?:Retrieved from\s+(https?://\S+?))?\.?$'

conference_presentation_18 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+Presentation at (?:the\s+)?(.+?),\s+(.+?),\s+([A-Z]{2}),\s+([A-Z]{2,3})\.?\s*(?:(https?://\S+?))?\.?$'

article_under_review_19 = r'^(.+?)\s+\((\d{4})\)\.\s+(.+?)\.\s+Manuscript submitted for review\.?$'


def extract_references(filename):
    reader = PdfReader(filename)
    req_content = ""
    flag = 0
    num_pg = len(reader.pages)

    for pgno in range(num_pg):
        page = reader.pages[pgno]
        content = page.extract_text()
        if flag == 1:
            req_content += content
        if "REFERENCES" in content:
            req_content += content.split("REFERENCES")[-1]
            flag = 1

    # Clean the extracted content
    req_content = req_content.strip().replace("\n", " ")

    # FIXED: Correct regex to split on reference numbers like [1], [2], etc.
    # The pattern \[\d+\] matches [1], [2], [3], etc.
    ref_list = re.split(r'\[\d+\]', req_content)

    # Clean each entry
    ref_list = [clean_reference(entry) for entry in ref_list if entry.strip()]

    return ref_list


def extract_authors(authors):
    """Extracts authors for 1, 2, and >2 authors"""
    if not authors:
        return []

    if "," in authors:
        author_list = authors.split(",")
        # Handle "and" in the last author
        if " and " in author_list[-1]:
            author_list[-1] = author_list[-1].split("and")[-1]
    else:
        author_list = authors.split(" and ")

    # Clean each author name
    author_list = [author.strip() for author in author_list]
    return author_list


def extract_year(ref):
    """Extracts year"""
    if len(ref) == 0:
        return None
    return ref[0].strip()


def extract_pages(field):
    """Extracts pages"""
    field = field.strip()
    res = re.findall(r"(\d+[–\-]\d+)", field)  # Handle both en-dash and hyphen
    if len(res) == 0:
        res = re.findall(r"(\d+)\s+pages?", field)
    return res[-1] if len(res) > 0 else None


def extract_title(ref):
    """Extracts title"""
    title = ref[0]
    return title.strip()


def extract_doi(field):
    """Extracts DOI"""
    field = field.strip().removeprefix("doi:")
    return field


def extract_edition(field):
    """Extracts edition number"""
    num = ""
    for char in field:
        if char.isnumeric():
            num += char
        else:
            break
    return int(num) if num else None


def parser(filepath):
    ref_list = extract_references(filepath)
    final_ref_list = []
    count = 1

    for entry in ref_list:
        dict_ref = {}
        dict_ref["id"] = count
        dict_ref["authors"] = None
        dict_ref["year"] = None
        dict_ref["title"] = None
        dict_ref["pages"] = None
        dict_ref["doi"] = None

        matched = False

        print(f"\n--- Processing Reference {count} ---")
        print(f"Entry: {entry[:100]}...")  # Print first 100 chars

        # For a paginated article in a journal
        match = re.match(pag_article_journal_1, entry)
        if match:
            print("✓ Matched: Journal Article (Paginated)")
            matched = True
            authors = match.group(1)
            year = match.group(2)
            title = match.group(3)
            journal = match.group(4)
            volume = match.group(5)
            issue = match.group(6)
            page_start = match.group(7)
            page_end = match.group(8)
            doi = match.group(
                9) if match.lastindex >= 9 and match.group(9) else None

            dict_ref["authors"] = extract_authors(
                authors)  # FIXED: Added authors argument
            dict_ref["year"] = int(year)
            dict_ref["title"] = title
            dict_ref["publication_type"] = "journal_article"
            dict_ref["journal_name"] = journal
            dict_ref["volume"] = int(volume)
            dict_ref["issue"] = int(issue)
            dict_ref["pages"] = f"{page_start}-{page_end}"
            dict_ref["doi"] = doi

        if not matched:
            match = re.match(enum_article_journal_2, entry)
            if match:
                print("✓ Matched: Journal Article (Article Number)")
                matched = True
                authors = match.group(1)
                year = match.group(2)
                title = match.group(3)
                journal = match.group(4)
                volume = match.group(5)
                issue = match.group(6)
                article = match.group(7)
                num_pages = match.group(8)
                doi = match.group(
                    9) if match.lastindex >= 9 and match.group(9) else None

                dict_ref["authors"] = extract_authors(authors)
                dict_ref["year"] = int(year)
                dict_ref["title"] = title
                dict_ref["publication_type"] = "journal_article"
                dict_ref["journal_name"] = journal
                dict_ref["volume"] = int(volume)
                dict_ref["issue"] = int(issue)
                dict_ref["article_number"] = int(article)
                dict_ref["pages"] = f"{num_pages} pages"
                dict_ref["doi"] = doi

        if not matched:
            match = re.match(monograph_book_3, entry)
            if match:
                print("✓ Matched: Monograph/Book")
                matched = True
                authors = match.group(1)
                year = match.group(2)
                title = match.group(3)
                edition = match.group(4)
                publisher = match.group(5)
                city = match.group(6)
                state = match.group(7) if match.lastindex >= 7 else None

                dict_ref["authors"] = extract_authors(authors)
                dict_ref["year"] = int(year)
                dict_ref["title"] = title
                dict_ref["publication_type"] = "monograph"
                dict_ref["edition"] = extract_edition(edition)
                dict_ref["publisher"] = publisher
                dict_ref["city"] = city
                dict_ref["state"] = state

        if not matched:
            match = re.match(arxiv_17, entry)
            if match:
                print("✓ Matched: arXiv")
                matched = True
                authors = match.group(1)
                year = match.group(2)
                title = match.group(3)
                arxiv_id = match.group(4)
                url = match.group(
                    5) if match.lastindex >= 5 and match.group(5) else None

                dict_ref["authors"] = extract_authors(authors)
                dict_ref["year"] = int(year)
                dict_ref["title"] = title
                dict_ref["publication_type"] = "arxiv"
                dict_ref["arxiv_id"] = arxiv_id
                dict_ref["url"] = url

        # Add similar blocks for other patterns...
        # (I'll include just a few more to show the pattern)

        if not matched:
            match = re.match(chap_edited_not_series_6, entry)
            if match:
                print("✓ Matched: Book Chapter")
                matched = True
                authors = match.group(1)
                year = match.group(2)
                chapter_title = match.group(3)
                book_title = match.group(4)
                editors = match.group(5)
                publisher = match.group(6)
                page_start = match.group(7)
                page_end = match.group(8)

                dict_ref["authors"] = extract_authors(authors)
                dict_ref["year"] = int(year)
                dict_ref["title"] = f"{chapter_title}, {book_title}"
                dict_ref["publication_type"] = "chapter_edited_book"
                dict_ref["editors"] = extract_authors(editors)
                dict_ref["publisher"] = publisher
                dict_ref["pages"] = f"{page_start}-{page_end}"

        if not matched:
            match = re.match(www_link_14, entry)
            if match:
                print("✓ Matched: Web Link (With Year)")
                matched = True
                organization = match.group(1)
                year = match.group(2)
                title = match.group(3)
                url = match.group(4)

                dict_ref["year"] = int(year)
                dict_ref["title"] = title
                dict_ref["publication_type"] = "online_document"
                dict_ref["organization"] = organization
                dict_ref["url"] = url

        if not matched:
            print("✗ No match found")

        final_ref_list.append(dict_ref)
        count += 1

    return final_ref_list


# MAIN EXECUTION
if __name__ == "__main__":
    filepath = "testfile3.pdf"  # FIXED: Define the filepath
    output = parser(filepath)

    # Print summary
    print(f"\n\n=== SUMMARY ===")
    print(f"Total references processed: {len(output)}")
    matched_count = sum(1 for ref in output if ref.get('publication_type'))
    print(f"Successfully matched: {matched_count}")
    print(f"Unmatched: {len(output) - matched_count}")

    # Print a few examples
    print("\n=== SAMPLE REFERENCES ===")
    for i, ref in enumerate(output[:3]):
        print(f"\nReference {i+1}:")
        print(f"  Type: {ref.get('publication_type', 'UNMATCHED')}")
        print(f"  Title: {ref.get('title', 'N/A')[:80]}...")
        print(f"  Year: {ref.get('year', 'N/A')}")
