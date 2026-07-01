# www resource 1
import re

pattern = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+\(([A-Za-z]+\s+\d{4})\)\.\s+Retrieved\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})\s+from\s+(https?://[^\s,]+),\s+archived at\s+\[(https?://[^\]]+)\]$'

# Test it
citation = "Harry Thornburg. 2001. Introduction to Bayesian Statistics. (March 2001). Retrieved March 2, 2005 from http://ccrma.stanford.edu/~jos/bayes/bayes.html, archived at [https://web.archive.org/web/20240505055615/https://ccrma.stanford.edu/~jos/bayes/bayes.html]"

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
