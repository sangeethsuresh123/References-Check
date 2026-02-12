# For a divisible book (anthology or compilation):
import re

pattern = r'^(.+?)\s+\(Ed\.\)\.\s+(\d{4})\.\s+(.+?)\s+\((\d+(?:st|nd|rd|th))\.\s+ed\.\)\.\s+(.+?),\s+Vol\.\s+(\d+)\.\s+(.+?),\s+(.+?)\.\s+(https?://doi\.org/[\d\.\/\-]+)$'

# Test it
citation = "Ian Editor (Ed.). 2007. The title of book one (1st. ed.). The name of the series one, Vol. 9. University of Chicago Press, Chicago. https://doi.org/10.1007/3-540-09237-4"

match = re.match(pattern, citation)

if match:
    editor = match.group(1)
    year = match.group(2)
    title = match.group(3)
    edition = match.group(4)
    series = match.group(5)
    volume = match.group(6)
    publisher = match.group(7)
    city = match.group(8)
    doi = match.group(9)

    print(f"Editor: {editor}")
    print(f"Year: {year}")
    print(f"Title: {title}")
    print(f"Edition: {edition}")
    print(f"Series: {series}")
    print(f"Volume: {volume}")
    print(f"Publisher: {publisher}")
    print(f"City: {city}")
    print(f"DOI: {doi}")
