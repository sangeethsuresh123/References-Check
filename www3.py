# www resource-3
import re

pattern = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+Retrieved from\s+(https?://[^\s]+)$'

# Test it
citation = "Wikipedia. 2017. WikipediA: the Free Encyclopedia. Retrieved from https://www.wikipedia.org/"

match = re.match(pattern, citation)

if match:
    organization = match.group(1)
    year = match.group(2)
    title = match.group(3)
    url = match.group(4)

    print(f"Organization: {organization}")
    print(f"Year: {year}")
    print(f"Title: {title}")
    print(f"URL: {url}")
