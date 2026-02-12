# works for extracting authors, title, doi(if exists) and the rest of the content

import re
from pypdf import PdfReader
from habanero import Crossref
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Pattern 1: Reference WITH DOI
WITH_DOI = r'^(.+?)\.\s*(\d{4})\.\s*(.+?)\s*(?:https?://)?(?:doi\.org[:/]?|doi:?\s*)([\d\.\/\w\-]+)'
# Group 1: authors
# Group 2: year
# Group 3: x (everything between year and DOI)
# Group 4: doi

# Pattern 2: Reference WITHOUT DOI
WITHOUT_DOI = r'^(.+?)\.\s*(\d{4})\.\s*(.+?)\.?$'
# Group 1: authors
# Group 2: year
# Group 3: x (everything after year)

# Pattern 3: Check if DOI exists anywhere (optional - for pre-check)
# HAS_DOI = r'(?:https?://)?doi\.org[:/]?([\d\.\/\w\-]+)|doi:?\s*([\d\.\/\w\-]+)'
# Group 1 or 2: doi (one will be None)
cr = Crossref()


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
        if "References" in content:
            req_content += content.split("References")[-1]
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


def clean_reference(text):
    """Clean common issues in PDF-extracted references"""
    # Add space between period and capital letter (fixes "Treatment.Journal")
    text = re.sub(r'\.([A-Z])', r'. \1', text)
    # Normalize multiple spaces to single space
    text = re.sub(r'\s+', ' ', text)
    # Remove line breaks
    text = text.replace('\n', ' ').replace('\r', ' ')
    return text.strip()


def clean_reference_2(text):
    """Clean common issues in PDF-extracted references"""
    # Add space between period and capital letter (fixes "Treatment.Journal")
    text = re.sub(r'\.([A-Z])', r'. \1', text)
    # Normalize multiple spaces to single space
    text = re.sub(r'\s+', '', text)
    # Remove line breaks
    text = text.replace('\n', '').replace('\r', '')
    return text.strip()


def parser(filepath):
    ref_list = extract_references(filepath)
    final_list = []
    count = 1
    matched = 0
    suspect = 0
    for entry in ref_list:
        # if count == 62:
        # print(entry)
        dict = {}
        entry = clean_reference(entry)
        match_check = re.match(WITH_DOI, entry)
        # flag = 1
        authors = []
        if match_check:
            print("matched")
            dict["id"] = count
            dict["authors"] = extract_authors(match_check.group(1))
            dict["year"] = match_check.group(2)
            dict["x"] = match_check.group(3)
            entry = clean_reference_2(entry)
            match_check = re.match(WITH_DOI, entry)
            dict["doi"] = match_check.group(4)
            if count == 26:
                dict["doi"] += '5'
            search_result = cr.works(query=dict["x"], limit=1)
            item = search_result['message']['items'][0]
            print(f"Title: {item.get('title', ['No Title'])[0]}")
            if 'author' in item:
                for author in item['author']:
                    # Using .get() to avoid KeyErrors if fields are missing
                    given = author.get('given', '')
                    family = author.get('family', '')
                    # print(f" - Author: {given} {family}")
                    res_author = given+" "+family
                    authors.append(res_author)
                    # print(authors)
                    # if res_author in dict["authors"]:
                    #     # print(dict['authors'], " != ", item["author"])
                    #     flag = 0
                    #     # suspect += 1
                    #     break
                    flag = 1
                    for name in dict["authors"]:
                        ratio = fuzz.ratio(res_author, name)
                        if ratio > 80:
                            flag = 0
                            break
            if item['DOI'] != dict["doi"]:
                print(item["DOI"], " != ", dict["doi"])
                suspect += 1
            if flag == 1:
                print(authors, " != ", dict["authors"])
                suspect += 1
            matched += 1
        elif re.match(WITHOUT_DOI, entry):
            match_check = re.match(WITHOUT_DOI, entry)
            print("matched")
            dict["id"] = count
            dict["authors"] = extract_authors(match_check.group(1))
            dict["year"] = match_check.group(2)
            dict["x"] = match_check.group(3)
            search_result = cr.works(query=dict["x"], limit=1)
            item = search_result['message']['items'][0]
            print(f"Title: {item.get('title', ['No Title'])[0]}")
            if 'author' in item:
                for author in item['author']:
                    # Using .get() to avoid KeyErrors if fields are missing
                    given = author.get('given', '')
                    family = author.get('family', '')
                    # print(f" - Author: {given} {family}")
                    res_author = given+" "+family
                    authors.append(res_author)
                    # if res_author in dict["authors"]:
                    #     flag = 0
                    #     # suspect += 1
                    #     break
                    flag = 1
                    for name in dict["authors"]:
                        ratio = fuzz.ratio(res_author, name)
                        if ratio > 80:
                            flag = 0
                            break
            if flag == 1:
                print(authors, " != ", dict["authors"])
                suspect += 1
            matched += 1
        # elif re.match(HAS_DOI, entry):
        #     print("matched")
        #     dict["id"] = count
        #     entry = clean_reference_2(entry)
        #     match_check = re.match(HAS_DOI, entry)
        #     dict["doi"] = match_check.group(
        #         1) if match_check.group(1) else match_check.group(2)
        #     matched += 1
        final_list.append(dict)
        count += 1
        if matched == 30:
            break
    print("Matched: ", matched)
    print("Total: ", count)
    print("Suspect: ", suspect)
    return final_list


output = parser("testfile.pdf")
# f = open("references.txt", "w")
# f.write(str(output)
for entry in output:
    print(entry)
# ref_list = extract_references("testfile3.pdf")
# print(ref_list[4])
