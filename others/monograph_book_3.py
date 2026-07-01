# For a monograph (whole book):
import re

pattern = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\s+\((\d+(?:st|nd|rd|th))\.\s+ed\.\)\.\s+(.+?),\s+(.+?),\s+([A-Z]{2})\.$'

# Test it
citation = "David Kosiur. 2001. Understanding Policy-Based Networking (2nd. ed.). Wiley, New York, NY."

match = re.match(pattern, citation)

if match:
    authors = match.group(1)
    year = match.group(2)
    title = match.group(3)
    edition = match.group(4)
    publisher = match.group(5)
    city = match.group(6)
    state = match.group(7)

    print(f"Authors: {authors}")
    print(f"Year: {year}")
    print(f"Title: {title}")
    print(f"Edition: {edition}")
    print(f"Publisher: {publisher}")
    print(f"City: {city}")
    print(f"State: {state}")
