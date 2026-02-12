# For a (paginated proceedings) article in a conference proceedings (conference, symposium or workshop):
import re

pattern = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+In\s+Proceedings of the (.+?)\s+\(([A-Z]+\s+\'\d{2})\),\s+([A-Za-z]+\s+\d{1,2}\s+-\s+\d{1,2},\s+\d{4}),\s+(.+?)\.\s+(.+?),\s+(.+?),\s+([A-Z]{2}),\s+(\d+)-(\d+)\.\s+(https?://doi\.org/[\d\.\/]+)$'

# Test it
citation = "Sten Andler. 1979. Predicate path expressions. In Proceedings of the 6th. ACM SIGACT-SIGPLAN Symposium on Principles of Programming Languages (POPL '79), January 29 - 31, 1979,  San Antonio, Texas. ACM Inc., New York, NY, 226-236. https://doi.org/10.1145/567752.567774"

match = re.match(pattern, citation)

if match:
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

    print(f"Authors: {authors}")
    print(f"Year: {year}")
    print(f"Title: {title}")
    print(f"Conference: {conference}")
    print(f"Abbreviation: {abbreviation}")
    print(f"Dates: {dates}")
    print(f"Location: {location}")
    print(f"Publisher: {publisher}")
    print(f"City: {city}")
    print(f"State: {state}")
    print(f"Pages: {page_start}-{page_end}")
    print(f"DOI: {doi}")
