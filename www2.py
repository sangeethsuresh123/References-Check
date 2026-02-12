# www resource-2
import re

pattern = r'^(.+?)\.\s+(.+?)\.\s+Retrieved from\s+(https?://[^\s]+)$'

# Test it
citation = "ACM. Association for Computing Machinery: Advancing Computing as a Science & Profession. Retrieved from http://www.acm.org/"

match = re.match(pattern, citation)

if match:
    organization = match.group(1)
    title = match.group(2)
    url = match.group(3)

    print(f"Organization: {organization}")
    print(f"Title: {title}")
    print(f"URL: {url}")
