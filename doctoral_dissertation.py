# Doctoral dissertation:
import re

pattern = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\s+\((.+?)\)\.\s+(Ph\.D\.|Master\'s)\s+Dissertation\.\s+(.+?),\s+(.+?),\s+([A-Z]{2})\.\s+UMI Order Number:\s+([A-Z]+\s+\d+)\.$'

# Test it
citation = "Kenneth L. Clarkson. 1985. Algorithms for Closest-Point Problems (Computational Geometry). Ph.D. Dissertation. Stanford University, Palo Alto, CA. UMI Order Number: AAT 8506171."

match = re.match(pattern, citation)

if match:
    authors = match.group(1)
    year = match.group(2)
    title = match.group(3)
    subject = match.group(4)
    degree = match.group(5)
    university = match.group(6)
    city = match.group(7)
    state = match.group(8)
    umi_number = match.group(9)

    print(f"Authors: {authors}")
    print(f"Year: {year}")
    print(f"Title: {title}")
    print(f"Subject: {subject}")
    print(f"Degree: {degree}")
    print(f"University: {university}")
    print(f"City: {city}")
    print(f"State: {state}")
    print(f"UMI Order Number: {umi_number}")
