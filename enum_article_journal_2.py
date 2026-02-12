# For an enumerated article in a journal:
import re

pattern = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(.+?)\s+(\d+),\s+(\d+),\s+Article\s+(\d+)\s+\(([A-Za-z]+)\s+\d{4}\),\s+(\d+)\s+pages?\.\s+(https?://doi\.org/[\d\.\/]+)$'

# Test it
citation = "Sarah Cohen, Werner Nutt, and Yehoshua Sagic. 2007. Deciding equivalences among conjunctive aggregate queries. J. ACM 54, 2, Article 5 (April 2007), 50 pages. https://doi.org/10.1145/1219092.1219093"

match = re.match(pattern, citation)

if match:
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
    print(type(volume))
    print(f"Authors: {authors}")
    print(f"Year: {year}")
    print(f"Title: {title}")
    print(f"Journal: {journal}")
    print(f"Volume: {volume}, Issue: {issue}")
    print(f"Article: {article}")
    print(f"Month: {month}")
    print(f"Pages: {num_pages}")
    print(f"DOI: {doi}")
