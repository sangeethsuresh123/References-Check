# video example 2
import re

pattern = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+Video\.\s+\((\d{1,2}\s+[A-Za-z]+\s+\d{4})\)\.\s+Retrieved\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})\s+from\s+(https?://[^\s,]+),\s+archived at\s+\[(https?://[^\]]+)\]$'

# Test it
citation = "Barack Obama. 2008. A more perfect union. Video. (5 March 2008). Retrieved March 21, 2008 from http://video.google.com/videoplay?docid=6528042696351994555, archived at [https://web.archive.org/web/20250310010326/https://www.youtube.com/watch?v=zrp-v2tHaDo]"

match = re.match(pattern, citation)

if match:
    authors = match.group(1)
    year = match.group(2)
    title = match.group(3)
    publication_date = match.group(4)
    retrieval_date = match.group(5)
    url = match.group(6)
    archive_url = match.group(7)

    print(f"Authors: {authors}")
    print(f"Year: {year}")
    print(f"Title: {title}")
    print(f"Publication Date: {publication_date}")
    print(f"Retrieved: {retrieval_date}")
    print(f"URL: {url}")
    print(f"Archive URL: {archive_url}")
