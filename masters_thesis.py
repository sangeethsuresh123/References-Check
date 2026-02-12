# Master's Thesis:
import re

pattern = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(Master\'s thesis|Ph\.D\. Dissertation)\.\s+(.+?),\s+(.+?),\s+(.+?)\.$'

# Test it
citation = "David A. Anisi. 2003. Optimal Motion Control of a Ground Vehicle. Master's thesis. Royal Institute of Technology (KTH), Stockholm, Sweden."

match = re.match(pattern, citation)

if match:
    authors = match.group(1)
    year = match.group(2)
    title = match.group(3)
    degree = match.group(4)
    university = match.group(5)
    city = match.group(6)
    country = match.group(7)

    print(f"Authors: {authors}")
    print(f"Year: {year}")
    print(f"Title: {title}")
    print(f"Degree: {degree}")
    print(f"University: {university}")
    print(f"City: {city}")
    print(f"Country: {country}")
