import re
from pypdf import PdfReader

# year_reg = "^([0-9]{4})$"
# pages_reg = "([0-9]+–[0-9]+)|([0-9]+ pages)"
# doi_reg = "10.[0-9]{4}/"
# content = ""
# pag_article_journal_1 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(.+?)\s+(\d+),\s+(\d+)\s+\(([A-Za-z]+)\.\s+\d{4}\),\s+(\d+)-(\d+)\.\s+(https?://doi\.org/[\d\.\/]+)$'
# enum_article_journal_2 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(.+?)\s+(\d+),\s+(\d+),\s+Article\s+(\d+)\s+\(([A-Za-z]+)\s+\d{4}\),\s+(\d+)\s+pages?\.\s+(https?://doi\.org/[\d\.\/]+)$'
# monograph_book_3 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\s+\((\d+(?:st|nd|rd|th))\.\s+ed\.\)\.\s+(.+?),\s+(.+?),\s+([A-Z]{2})\.$'
# divisible_book_4 = r'^(.+?)\s+\(Ed\.\)\.\s+(\d{4})\.\s+(.+?)\s+\((\d+(?:st|nd|rd|th))\.\s+ed\.\)\.\s+(.+?),\s+Vol\.\s+(\d+)\.\s+(.+?),\s+(.+?)\.\s+(https?://doi\.org/[\d\.\/\-]+)$'
# multi_vol_work_5 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?),\s+Vol\.\s+(\d+):\s+(.+?)\s+\((\d+(?:st|nd|rd|th))\.\s+ed\.\)\.\s+(.+?)\.$'
# chap_edited_not_series_6 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+In\s+(.+?)\.\s+(.+?)\s+\(Eds?\.\),\s+(.+?),\s+(\d+)–(\d+)\.$'
# article_conference_7 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+In\s+Proceedings of the (.+?)\s+\(([A-Z]+\s+\'\d{2})\),\s+([A-Za-z]+\s+\d{1,2}\s+-\s+\d{1,2},\s+\d{4}),\s+(.+?)\.\s+(.+?),\s+(.+?),\s+([A-Z]{2}),\s+(\d+)-(\d+)\.\s+(https?://doi\.org/[\d\.\/]+)$'
# patent_8 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+\(([A-Za-z]+)\.\s+(\d{4})\)\.\s+Patent No\.\s+(\d+),\s+Filed\s+(.+?),\s+Issued\s+(.+?)\.$'
# technical_report_9 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(.+?)\s+(Technical Report|TR)\s+([A-Z]+-\d+)\.\s+(.+?),\s+(.+?),\s+([A-Z]{2})\.$'
# doctoral_dissertation_10 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\s+\((.+?)\)\.\s+(Ph\.D\.|Master\'s)\s+Dissertation\.\s+(.+?),\s+(.+?),\s+([A-Z]{2})\.\s+UMI Order Number:\s+([A-Z]+\s+\d+)\.$'
# masters_thesis_11 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(Master\'s thesis|Ph\.D\. Dissertation)\.\s+(.+?),\s+(.+?),\s+(.+?)\.$'
# www_link_12 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+\(([A-Za-z]+\s+\d{4})\)\.\s+Retrieved\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})\s+from\s+(https?://[^\s,]+),\s+archived at\s+\[(https?://[^\]]+)\]$'
# www_link_13 = r'^(.+?)\.\s+(.+?)\.\s+Retrieved from\s+(https?://[^\s]+)$'
# www_link_14 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+Retrieved from\s+(https?://[^\s]+)$'
# video_link_15 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+Video\.\s+In\s+(.+?)\s+\(([A-Za-z]+\s+\d{1,2}-\d{1,2},\s+\d{4})\)\.\s+(.+?),\s+(.+?),\s+([A-Z]{2}),\s+(\d+)\.\s+(https?://doi\.org/[\d\.\/\w\-]+)$'
# video_link_16 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+Video\.\s+\((\d{1,2}\s+[A-Za-z]+\s+\d{4})\)\.\s+Retrieved\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})\s+from\s+(https?://[^\s,]+),\s+archived at\s+\[(https?://[^\]]+)\]$'
# arxiv_17 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+arXiv:([\d\.]+)\.\s+Retrieved from\s+(https?://[^\s]+)$'
# conference_presentation_18 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+Presentation at the\s+(.+?),\s+(.+?),\s+([A-Z]{2}),\s+([A-Z]{3})\.(?:\s*)(?:(https?://[^\s]+))?$'
# article_under_review_19 = r'^(.+?)\s+\((\d{4})\)\.\s+(.+?)\.\s+Manuscript submitted for review\.$'

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
    # req_content.strip()
    # req_content.replace("\n", " ")
    req_content = req_content.strip().replace("\n", " ")
    # ref_list = re.split("[.[0-9]+.]", req_content)
    ref_list = re.split(r'\[\d+\]', req_content)
    ref_list = [entry.strip() for entry in ref_list]
    ref_list = ref_list[1:]
    return ref_list


def extract_authors(authors):  # extracts authors for 1,2 and >2 authors
    if "," in authors:
        author_list = authors.split(",")
        author_list[-1] = author_list[-1].split("and")[-1]
    else:
        author_list = authors.split(" and ")

    for i in range(len(author_list)):
        author_list[i] = author_list[i].strip().replace("\n", " ")
    return author_list


def extract_year(ref):  # extracts year
    # print("in year: ", ref)
    if len(ref) == 0:
        return None
    return ref[0].strip()


def extract_pages(field):  # extracts pages
    field = field.strip()
    res = re.findall("([0-9]+–[0-9]+)", field)
    if len(res) == 0:
        res = re.findall("([0-9]+ pages)", field)
    return res[-1] if len(res) > 0 else None


def extract_title(ref):
    title = ref[0]
    return title.strip().replace("\n", " ")


def extract_doi(field):
    field = field.strip().removeprefix("doi:")
    return field


def extract_edition(field):
    num = ""
    for char in field:
        if char.isnumeric():
            num += char
        else:
            break
    return int(num)

# def parser(filepath):
#     ref_list, content = extract_references(filepath)
#     final_ref_list = []
#     count = 1
#     for entry in ref_list:

#         dict = {}
#         dict["id"] = count
#         dict["authors"] = None
#         dict["year"] = None
#         dict["title"] = None
#         dict["pages"] = None
#         dict["doi"] = None

#         dict["year"] = extract_year(re.findall("[0-9]{4}", entry))
#         ref = re.split(r"[0-9]{4}.", entry, maxsplit=1)
#         dict["authors"] = extract_authors(ref)
#         ref.pop(0)
#         ref = ref[0].split(". ")
#         dict["title"] = extract_title(ref)
#         ref.pop(0)
#         for field in ref:
#             field = field.replace("\n", "")
#             field = field.strip()
#             if re.search(pages_reg, field):
#                 dict["pages"] = extract_pages(field)
#             if re.search(doi_reg, field):
#                 dict["doi"] = extract_doi(field)
#         final_ref_list.append(dict)
#         count += 1

#     return final_ref_list


def clean_reference(text):
    """Clean common issues in PDF-extracted references"""
    # Add space between period and capital letter (fixes "Treatment.Journal")
    text = re.sub(r'\.([A-Z])', r'. \1', text)
    # Normalize multiple spaces to single space
    text = re.sub(r'\s+', ' ', text)
    # Remove line breaks
    text = text.replace('\n', ' ').replace('\r', ' ')
    return text.strip()


def parser(filepath):
    ref_list = extract_references(filepath)
    final_ref_list = []
    count = 1
    matched = 0
    for entry in ref_list:

        dict = {}
        dict["id"] = count
        dict["authors"] = None
        dict["year"] = None
        dict["title"] = None
        dict["pages"] = None
        dict["doi"] = None
        entry = clean_reference(entry)
        # print(entry)
        # For a paginated article in a journal
        match = re.match(pag_article_journal_1, entry)
        if match:
            matched += 1
            authors = match.group(1)
            year = match.group(2)
            title = match.group(3)
            journal = match.group(4)
            volume = match.group(5)
            issue = match.group(6)
            month = match.group(7)
            page_start = match.group(8)
            page_end = match.group(9)
            # doi = match.group(10) if match.group(10) else None

            dict["authors"] = extract_authors(authors)
            dict["year"] = int(year)
            dict["title"] = title
            dict["publication_type"] = "journal_article"
            dict["journal_name"] = journal
            dict["journal_abbreviation"] = None
            dict["volume"] = int(volume)
            dict["issue"] = int(issue)
            dict["article_number"] = None
            dict["month"] = month
            dict["pages"] = str(page_start)+"-"+str(page_end)
            # dict["doi"] = doi

        if not matched:
            match = re.match(enum_article_journal_2, entry)
            if match:
                matched += 1
                authors = match.group(1)
                year = match.group(2)
                title = match.group(3)
                journal = match.group(4)
                volume = match.group(5)
                issue = match.group(6)
                article = match.group(7)
                month = match.group(8)
                num_pages = match.group(9)
                doi = match.group(10)

                dict["authors"] = extract_authors(authors)
                dict["year"] = int(year)
                dict["title"] = title
                dict["publication_type"] = "journal_article"
                dict["journal_name"] = journal
                dict["journal_abbreviation"] = None
                dict["volume"] = int(volume)
                dict["issue"] = int(issue)
                dict["article_number"] = int(article)
                dict["month"] = month
                dict["pages"] = num_pages + " pages"
                dict["doi"] = doi

        if not matched:
            match = re.match(monograph_book_3, entry)

            if match:
                matched += 1
                authors = match.group(1)
                year = match.group(2)
                title = match.group(3)
                edition = match.group(4)
                publisher = match.group(5)
                city = match.group(6)
                state = match.group(7)

                dict["authors"] = extract_authors(authors)
                dict["year"] = int(year)
                dict["title"] = title
                dict["publication_type"] = "monograph"
                dict["edition"] = extract_edition(edition)
                dict["publisher"] = publisher
                dict["city"] = city
                dict["state"] = state

        if not matched:
            match = re.match(divisible_book_4, entry)

            if match:
                matched += 1
                editor = match.group(1)
                year = match.group(2)
                title = match.group(3)
                edition = match.group(4)
                series = match.group(5)
                volume = match.group(6)
                publisher = match.group(7)
                city = match.group(8)
                doi = match.group(9)

                dict["editor"] = extract_authors(editor)
                dict["year"] = int(year)
                dict["title"] = title
                dict["publication_type"] = "divisible_book"
                dict["edition"] = extract_edition(edition)
                dict["series"] = series
                dict["volume"] = int(volume)
                dict["publisher"] = publisher
                dict["city"] = city
                dict["doi"] = doi

        if not matched:
            match = re.match(multi_vol_work_5, entry)

            if match:
                matched += 1
                authors = match.group(1)
                year = match.group(2)
                title = match.group(3)
                volume = match.group(4)
                subtitle = match.group(5)
                edition = match.group(6)
                publisher = match.group(7)

                dict["authors"] = extract_authors(authors)
                dict["year"] = int(year)
                dict["title"] = title
                dict["publication_type"] = "multi_volume_work"
                dict["volume"] = int(volume)
                dict["subtitle"] = subtitle
                dict["edition"] = extract_edition(edition)
                dict["publisher"] = publisher

        if not matched:
            match = re.match(chap_edited_not_series_6, entry)

            if match:
                matched += 1
                authors = match.group(1)
                year = match.group(2)
                chapter_title = match.group(3)
                book_title = match.group(4)
                editors = match.group(5)
                publisher = match.group(6)
                page_start = match.group(7)
                page_end = match.group(8)

                dict["authors"] = extract_authors(authors)
                dict["year"] = int(year)
                dict["title"] = chapter_title + ", " + book_title
                dict["publication_type"] = "chapter_edited_book_not_series"
                dict["editors"] = extract_authors(editors)
                dict["publisher"] = publisher
                dict["pages"] = str(page_start)+"-"+str(page_end)

        if not matched:
            match = re.match(article_conference_7, entry)

            if match:
                matched += 1
                authors = match.group(1)
                year = match.group(2)
                title = match.group(3)
                conference = match.group(4)
                abbreviation = match.group(5)
                dates = match.group(6)
                location = match.group(7)
                publisher = match.group(8)
                city = match.group(9)
                state = match.group(10)
                page_start = match.group(11)
                page_end = match.group(12)
                doi = match.group(13)

                dict["authors"] = extract_authors(authors)
                dict["year"] = int(year)
                dict["title"] = title
                dict["publication_type"] = "conference_paper"
                dict["conference_name"] = conference
                dict["conference_acronym"] = abbreviation
                dict["edition"] = None
                dict["pages"] = str(page_start)+"-"+str(page_end)
                dict["publisher"] = publisher
                dict["doi"] = doi
                dict["dates"] = dates
                dict["location"] = location
                dict["city"] = city
                dict["state"] = state

        if not matched:
            match = re.match(patent_8, entry)

            if match:
                matched += 1
                inventor = match.group(1)
                year = match.group(2)
                title = match.group(3)
                month = match.group(4)
                year_in_parens = match.group(5)
                patent_number = match.group(6)
                filed_date = match.group(7)
                issued_date = match.group(8)

                dict["inventor"] = extract_authors(inventor)
                dict["year"] = int(year)
                dict["title"] = title
                dict["publication_type"] = "patent"
                dict["month"] = month
                dict["patent_number"] = patent_number
                dict["filed_date"] = filed_date
                dict["issued_date"] = issued_date

        if not matched:
            match = re.match(technical_report_9, entry)

            if match:
                matched += 1
                authors = match.group(1)
                year = match.group(2)
                title = match.group(3)
                institution_dept = match.group(4)
                report_type = match.group(5)
                report_number = match.group(6)
                institution = match.group(7)
                city = match.group(8)
                state = match.group(9)

                dict["authors"] = extract_authors(authors)
                dict["year"] = int(year)
                dict["title"] = title
                dict["publication_type"] = "technical_report"
                dict["department"] = institution_dept
                dict["report_number"] = report_number
                dict["institution"] = institution
                dict["city"] = city
                dict["state"] = state

        if not matched:
            match = re.match(doctoral_dissertation_10, entry)

            if match:
                matched += 1
                authors = match.group(1)
                year = match.group(2)
                title = match.group(3)
                subject = match.group(4)
                degree = match.group(5)
                university = match.group(6)
                city = match.group(7)
                state = match.group(8)
                umi_number = match.group(9)

                dict["authors"] = extract_authors(authors)
                dict["year"] = int(year)
                dict["title"] = title
                dict["publication_type"] = "doctoral_dissertation"
                dict["subject"] = subject
                dict["degree"] = degree
                dict["university"] = university
                dict["city"] = city
                dict["state"] = state
                dict["umi_number"] = umi_number

        if not matched:
            match = re.match(masters_thesis_11, entry)

            if match:
                matched += 1
                authors = match.group(1)
                year = match.group(2)
                title = match.group(3)
                degree = match.group(4)
                university = match.group(5)
                city = match.group(6)
                country = match.group(7)

                dict["authors"] = extract_authors(authors)
                dict["year"] = int(year)
                dict["title"] = title
                dict["publication_type"] = "masters_thesis"
                dict["degree"] = degree
                dict["university"] = university
                dict["city"] = city
                dict["country"] = country

        if not matched:
            match = re.match(www_link_12, entry)

            if match:
                matched += 1
                authors = match.group(1)
                year = match.group(2)
                title = match.group(3)
                publication_date = match.group(4)
                retrieval_date = match.group(5)
                url = match.group(6)
                archive_url = match.group(7)

                dict["authors"] = extract_authors(authors)
                dict["year"] = int(year)
                dict["title"] = title
                dict["publication_type"] = "online_document"
                dict["publication_date"] = publication_date
                dict["retrieval_date"] = retrieval_date
                dict["url"] = url
                dict["archive_url"] = archive_url

        if not matched:
            match = re.match(www_link_13, entry)

            if match:
                matched += 1
                organization = match.group(1)
                title = match.group(2)
                url = match.group(3)

                dict["title"] = title
                dict["publication_type"] = "online_document"
                dict["organization"] = organization
                dict["url"] = url

        if not matched:
            match = re.match(www_link_14, entry)

            if match:
                matched += 1
                organization = match.group(1)
                year = match.group(2)
                title = match.group(3)
                url = match.group(4)

                dict["year"] = int(year)
                dict["title"] = title
                dict["publication_type"] = "online_document"
                dict["organization"] = organization
                dict["url"] = url

        if not matched:
            match = re.match(video_link_15, entry)

            if match:
                matched += 1
                authors = match.group(1)
                year = match.group(2)
                title = match.group(3)
                collection = match.group(4)
                dates = match.group(5)
                publisher = match.group(6)
                city = match.group(7)
                state = match.group(8)
                item_number = match.group(9)
                doi = match.group(10)

                dict["authors"] = extract_authors(authors)
                dict["year"] = int(year)
                dict["title"] = title
                dict["publication_type"] = "video_resource"
                dict["collection"] = collection
                dict["dates"] = dates
                dict["publisher"] = publisher
                dict["city"] = city
                dict["state"] = state
                dict["item_number"] = int(item_number)
                dict["doi"] = doi

        if not matched:
            match = re.match(video_link_16, entry)

            if match:
                matched += 1
                authors = match.group(1)
                year = match.group(2)
                title = match.group(3)
                publication_date = match.group(4)
                retrieval_date = match.group(5)
                url = match.group(6)
                archive_url = match.group(7)

                dict["authors"] = extract_authors(authors)
                dict["year"] = int(year)
                dict["title"] = title
                dict["publication_type"] = "video_resource"
                dict["publication_date"] = publication_date
                dict["retrieval_date"] = retrieval_date
                dict["url"] = url
                dict["archive_url"] = archive_url

        if not matched:
            match = re.match(arxiv_17, entry)

            if match:
                matched += 1
                authors = match.group(1)
                year = match.group(2)
                title = match.group(3)
                arxiv_id = match.group(4)
                url = match.group(5)

                dict["authors"] = extract_authors(authors)
                dict["year"] = int(year)
                dict["title"] = title
                dict["publication_type"] = "arxiv"
                dict["arxiv_id"] = arxiv_id
                dict["url"] = url

        if not matched:
            match = re.match(conference_presentation_18, entry)

            if match:
                matched += 1
                authors = match.group(1)
                year = match.group(2)
                title = match.group(3)
                event = match.group(4)
                city = match.group(5)
                state = match.group(6)
                country = match.group(7)
                url = match.group(8) if match.group(8) else None

                dict["authors"] = extract_authors(authors)
                dict["year"] = int(year)
                dict["title"] = title
                dict["publication_type"] = "conference_presentation"
                dict["event"] = event
                dict["city"] = city
                dict["state"] = state
                dict["country"] = country
                dict["url"] = url

        if not matched:
            match = re.match(article_under_review_19, entry)

            if match:
                matched += 1
                authors = match.group(1)
                year = match.group(2)
                title = match.group(3)

                dict["authors"] = extract_authors(authors)
                dict["year"] = int(year)
                dict["title"] = title
                dict["publication_type"] = "article_under_review"
        # else:
        #     print("No match found")
        final_ref_list.append(dict)
        count += 1
    print("Matched: ", matched)
    return final_ref_list


output = parser("testfile3.pdf")
# f = open("references.txt", "w")
# f.write(str(output))
print(output)
# ref_list = extract_references("testfile3.pdf")
# print(ref_list[4])
