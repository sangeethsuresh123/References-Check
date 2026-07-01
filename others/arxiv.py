# for arxiv
import re

pattern = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+arXiv:([\d\.]+)\.\s+Retrieved from\s+(https?://[^\s]+)$'

# Test it
citation = "Martha Constantinou. 2016. New physics searches from nucleon matrix elements in lattice QCD.  arXiv:1701.00133. Retrieved from https://arxiv.org/abs/1701.00133"

match = re.match(pattern, citation)

if match:
    authors = match.group(1)
    year = match.group(2)
    title = match.group(3)
    arxiv_id = match.group(4)
    url = match.group(5)

    print(f"Authors: {authors}")
    print(f"Year: {year}")
    print(f"Title: {title}")
    print(f"arXiv ID: {arxiv_id}")
    print(f"URL: {url}")
