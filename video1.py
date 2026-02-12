# video example 1
import re

pattern = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+Video\.\s+In\s+(.+?)\s+\(([A-Za-z]+\s+\d{1,2}-\d{1,2},\s+\d{4})\)\.\s+(.+?),\s+(.+?),\s+([A-Z]{2}),\s+(\d+)\.\s+(https?://doi\.org/[\d\.\/\w\-]+)$'

# Test it
citation = "Dave Novak. 2003. Solder man. Video. In ACM SIGGRAPH 2003 Video Review on Animation theater Program: Part I - Vol. 145 (July 27-27, 2003). ACM Press, New York, NY, 4. https://doi.org/99.9999/woot07-S422"

match = re.match(pattern, citation)

if match:
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

    print(f"Authors: {authors}")
    print(f"Year: {year}")
    print(f"Title: {title}")
    print(f"Collection: {collection}")
    print(f"Dates: {dates}")
    print(f"Publisher: {publisher}")
    print(f"City: {city}")
    print(f"State: {state}")
    print(f"Item Number: {item_number}")
    print(f"DOI: {doi}")
