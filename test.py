import re
from pypdf import PdfReader

from habanero import Crossref
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# def extract_references(filename):
#     reader = PdfReader(filename)
#     req_content = ""
#     flag = 0
#     num_pg = len(reader.pages)
#     for pgno in range(num_pg):
#         page = reader.pages[pgno]
#         content = page.extract_text()
#         if flag == 1:
#             req_content += content
#         if "References" in content:
#             req_content += content.split("References")[-1]
#             flag = 1
#     # req_content = req_content.strip().replace("\n", " ")
#     ref_list = re.split("[.[0-9]+.]", req_content)
#     ref_list = ref_list[1:]
#     return ref_list


# def extract_authors(ref):  # extracts authors for 1,2 and >2 authors
#     authors = ref[0]
#     if "," in authors:
#         author_list = authors.split(",")
#         author_list[-1] = author_list[-1].split("and")[-1]
#     else:
#         author_list = authors.split(" and ")

#     for i in range(len(author_list)):
#         author_list[i] = author_list[i].strip().replace("\n", " ")
#     return author_list


# def extract_year(ref):
#     print("in year: ", ref)  # extracts year
#     if len(ref) == 0:
#         return None
#     return ref[0].strip()


# # def extract_pages(field):  # extracts year
# #     field = field.strip()
# #     res = re.findall(pages_reg, field)
# #     return res[-1] if len(res) > 0 else None
# def extract_pages(field):  # extracts pages
#     field = field.strip()
#     res = re.findall("([0-9]+–[0-9]+)", field)
#     if len(res) == 0:
#         res = re.findall("([0-9]+ pages)", field)
#     return res[-1] if len(res) > 0 else None


# def extract_title(ref):
#     title = ref[0]
#     return title.strip().replace("\n", " ")


# def extract_doi(field):
#     field = field.strip().removeprefix("doi:")
#     return field


# year_reg = "^([0-9]{4})$"
# # pages_reg = "([0-9]+–[0-9]+)"
# pages_reg = "([0-9]+–[0-9]+)|([0-9]+ pages)"
# ref_list = extract_references("testfile.pdf")
# dict = {}
# dict["year"] = extract_year(re.findall("[0-9]{4}", ref_list[25]))
# ref = re.split(r"[0-9]{4}.", ref_list[25], maxsplit=1)
# print(ref)
# # year_reg = "^([0-9]{4})$"
# doi_reg = "10.[0-9]{4}/"
# dict["authors"] = extract_authors(ref)
# ref.pop(0)
# ref = ref[0].split(". ")
# dict["title"] = extract_title(ref)
# ref.pop(0)
# # print(ref)
# for field in ref:
#     # if re.search(year_reg, field.strip()):
#     #     dict["year"] = extract_year(field)
#     #     print(dict["year"])
#     if re.search(pages_reg, field):
#         dict["pages"] = extract_pages(field)
#         print(dict["pages"])
#     if re.search(doi_reg, field):
#         dict["doi"] = extract_doi(field)
# # print(dict)
# print(int("23rd"))


# # Helper function to clean references

# def clean_reference(text):
#     """Clean common issues in PDF-extracted references"""
#     # Add space between period and capital letter (fixes "Treatment.Journal")
#     text = re.sub(r'\.([A-Z])', r'. \1', text)
#     # Normalize multiple spaces to single space
#     text = re.sub(r'\s+', ' ', text)
#     # Remove line breaks
#     text = text.replace('\n', ' ').replace('\r', ' ')
#     # Trim whitespace
#     return text.strip()


# # UPDATED REGEX PATTERNS - with flexible spacing and en-dash support
# pag_article_journal_1 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(.+?)\s+(\d+),\s+(\d+)\s+\((?:[A-Za-z]+\.?\s+)?\d{4}\),\s+(\d+)[–\-](\d+)\.?\s*(?:https?://doi\.org/([\d\.\/]+))?$'

# enum_article_journal_2 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(.+?)\s+(\d+),\s+(\d+),\s+Article\s+(\d+)\s+\((?:[A-Za-z]+\.?\s+)?\d{4}\),\s+(\d+)\s+pages?\.?\s*(?:https?://doi\.org/([\d\.\/]+))?$'

# monograph_book_3 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\s+\((\d+(?:st|nd|rd|th))\.?\s+ed\.?\)\.\s+(.+?),\s+(.+?)(?:,\s+([A-Z]{2}))?\.?$'

# divisible_book_4 = r'^(.+?)\s+\(Eds?\.?\)\.\s+(\d{4})\.\s+(.+?)\s+\((\d+(?:st|nd|rd|th))\.?\s+ed\.?\)\.\s+(.+?),\s+Vol\.?\s+(\d+)\.\s+(.+?),\s+(.+?)\.?\s*(?:https?://doi\.org/([\d\.\/\-]+))?$'

# multi_vol_work_5 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?),\s+Vol\.?\s+(\d+):\s+(.+?)\s+\((\d+(?:st|nd|rd|th))\.?\s+ed\.?\)\.\s+(.+?)\.?$'

# chap_edited_not_series_6 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+In\s+(.+?)\.\s+(.+?)\s+\(Eds?\.?\),\s+(.+?),\s+(\d+)[–\-](\d+)\.?$'

# article_conference_7 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+In\s+(?:Proceedings of the\s+)?(.+?)\s+\(([A-Z]+\s*\'?\d{2})\),\s+([A-Za-z]+\s+\d{1,2}\s*[–\-]\s*\d{1,2},\s+\d{4}),\s+(.+?)\.\s+(.+?),\s+(.+?),\s+([A-Z]{2}),\s+(\d+)[–\-](\d+)\.?\s*(?:https?://doi\.org/([\d\.\/]+))?$'

# patent_8 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+\(([A-Za-z]+\.?\s+\d{4})\)\.\s+Patent No\.?\s+(\d+),\s+Filed\s+(.+?),\s+Issued\s+(.+?)\.?$'

# technical_report_9 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(.+?)\s+(Technical Report|TR)\s+([A-Z]+-?\d+)\.\s+(.+?),\s+(.+?)(?:,\s+([A-Z]{2}))?\.?$'

# doctoral_dissertation_10 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\s+\((.+?)\)\.\s+(Ph\.?D\.?|Master\'?s)\s+Dissertation\.\s+(.+?),\s+(.+?),\s+([A-Z]{2})\.\s+UMI Order Number:\s+([A-Z]+\s+\d+)\.?$'

# masters_thesis_11 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(Master\'?s\s+thesis|Ph\.?D\.?\s+Dissertation)\.\s+(.+?),\s+(.+?),\s+(.+?)\.?$'

# www_link_12 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+\(([A-Za-z]+\.?\s+\d{4})\)\.\s+Retrieved\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})\s+from\s+(https?://[^\s,]+),?\s*archived at\s+\[?(https?://[^\]\s]+)\]?\.?$'

# www_link_13 = r'^(.+?)\.\s+(.+?)\.\s+Retrieved from\s+(https?://\S+?)\.?$'

# www_link_14 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+Retrieved from\s+(https?://\S+?)\.?$'

# video_link_15 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+Video\.\s+In\s+(.+?)\s+\(([A-Za-z]+\s+\d{1,2}[–\-]\d{1,2},\s+\d{4})\)\.\s+(.+?),\s+(.+?),\s+([A-Z]{2}),\s+(\d+)\.?\s*(?:https?://doi\.org/([\d\.\/\w\-]+))?$'

# video_link_16 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+Video\.\s+\((\d{1,2}\s+[A-Za-z]+\s+\d{4})\)\.\s+Retrieved\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})\s+from\s+(https?://[^\s,]+),?\s*archived at\s+\[?(https?://[^\]\s]+)\]?\.?$'

# arxiv_17 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s*arXiv\s*(?:preprint\s+)?arXiv:([\d\.]+)(?:\s+\(\d{4}\))?\.?\s*(?:Retrieved from\s+(https?://\S+?))?\.?$'

# conference_presentation_18 = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+Presentation at (?:the\s+)?(.+?),\s+(.+?),\s+([A-Z]{2}),\s+([A-Z]{2,3})\.?\s*(?:(https?://\S+?))?\.?$'

# article_under_review_19 = r'^(.+?)\s+\((\d{4})\)\.\s+(.+?)\.\s+Manuscript submitted for review\.?$'
# cr = Crossref()
# query_result = cr.works(query="Au- toCodeRover: Autonomous Program Improvement. InProceedings of the 33rd ACM SIGSOFT International Symposium on Software Testing and Analysis(Vienna, Austria)(ISSTA 2024). Association for Computing Machinery, New York, NY, USA, 1592–1604.")
# # The results are returned as a dictionary, the actual data is in 'message' -> 'items'
# print("Query Result:")
# # print(query_result)
# items = query_result['message']['items']
# print("\nItems:")
# # print(items)
# print(items[0])
# print(f"Found {query_result['message']['total-results']} results.")
# print(f"First result DOI: {items[0]['DOI']}")
# # print("DOI specified: 10.1145/3650212.3680384")

# Search for works (e.g., query "ecology")
# Limit results to 2 for this example
# result = cr.works(query="ecology", limit=2)
# authors = ['An Ran Chen', 'Tse-Hsun Chen', 'Junjie Chen']
# result = cr.works(
#     query="How Useful is Code Change Information for Fault Localization in Continuous Integration?. InProceedings of the 37th IEEE/ACM International Conference on Automated Software Engineering. 1–12", limit=1)

# # Extract and print author names
# item = result['message']['items'][0]
# res_authors = []
# print(f"Title: {item.get('title', ['No Title'])[0]}")
# if 'author' in item:
#     for author in item['author']:
#         # Using .get() to avoid KeyErrors if fields are missing
#         given = author.get('given', '')
#         family = author.get('family', '')
#         # print(f" - Author: {given} {family}")
#         res_author = given+" "+family
#         res_authors.append(res_author)
#         print(res_author)
#         if res_author in authors:
#             print("Yes")
#         else:
#             print("No")
# else:
#     print(" - No authors listed")
#     print("-" * 20)
# print(res_authors)

s1 = 'Vincent Cicirello'
s2 = 'Vincent A Cicirello'
ratio = fuzz.ratio(s1, s2)
print(ratio)
