# For a multi-volume work (as a book):
import re

pattern = r'^(.+?)\.\s+(\d{4})\.\s+(.+?),\s+Vol\.\s+(\d+):\s+(.+?)\s+\((\d+(?:st|nd|rd|th))\.\s+ed\.\)\.\s+(.+?)\.$'

# Test it
citation = "Donald E. Knuth. 1997. The Art of Computer Programming, Vol. 1: Fundamental Algorithms (3rd. ed.). Addison Wesley Longman Publishing Co., Inc."

match = re.match(pattern, citation)

if match:
    authors = match.group(1)
    year = match.group(2)
    title = match.group(3)
    volume = match.group(4)
    subtitle = match.group(5)
    edition = match.group(6)
    publisher = match.group(7)

    print(f"Authors: {authors}")
    print(f"Year: {year}")
    print(f"Title: {title}")
    print(f"Volume: {volume}")
    print(f"Subtitle: {subtitle}")
    print(f"Edition: {edition}")
    print(f"Publisher: {publisher}")
