# For a chapter in an edited book that is not part of a series:
import re

pattern = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+In\s+(.+?)\.\s+(.+?)\s+\(Eds?\.\),\s+(.+?),\s+(\d+)–(\d+)\.$'

# Test it
citation = "Beth Warren, Shirin Vossoughi, Ann S. Rosebery, Megan Bang, and Edd V. Taylor. 2020. Multiple ways of knowing*: Re-imagining disciplinary learning. In Handbook of the Cultural Foundations of Learning. Na'ilah Suad Nasir, Carol D. Lee, Roy Pea, and Maxine McKinney de Royston (Eds.), Routledge, 277–294."

match = re.match(pattern, citation)

if match:
    authors = match.group(1)
    year = match.group(2)
    chapter_title = match.group(3)
    book_title = match.group(4)
    editors = match.group(5)
    publisher = match.group(6)
    page_start = match.group(7)
    page_end = match.group(8)

    print(f"Authors: {authors}")
    print(f"Year: {year}")
    print(f"Chapter Title: {chapter_title}")
    print(f"Book Title: {book_title}")
    print(f"Editors: {editors}")
    print(f"Publisher: {publisher}")
    print(f"Pages: {page_start}–{page_end}")
