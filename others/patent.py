# For a Patent:
import re

pattern = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+\(([A-Za-z]+)\.\s+(\d{4})\)\.\s+Patent No\.\s+(\d+),\s+Filed\s+(.+?),\s+Issued\s+(.+?)\.$'

# Test it
citation = "Joseph Scientist. 2009. The fountain of youth. (Aug. 2009). Patent No. 12345, Filed July 1st., 2008, Issued Aug. 9th., 2009."

match = re.match(pattern, citation)

if match:
    inventor = match.group(1)
    year = match.group(2)
    title = match.group(3)
    month = match.group(4)
    year_in_parens = match.group(5)
    patent_number = match.group(6)
    filed_date = match.group(7)
    issued_date = match.group(8)

    print(f"Inventor: {inventor}")
    print(f"Year: {year}")
    print(f"Title: {title}")
    print(f"Month: {month}")
    print(f"Patent Number: {patent_number}")
    print(f"Filed Date: {filed_date}")
    print(f"Issued Date: {issued_date}")
else:
    print("No match found")
