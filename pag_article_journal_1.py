# For a paginated article in a journal:
import re
pattern = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(.+?)\s+(\d+),\s+(\d+)\s+\(\s+\d{4}\),\s+(\d+)-(\d+)\.\s+(https?://doi\.org/[\d\.\/]+)$'
# pattern = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(.+?)\s+(\d+),\s+(\d+)\s+\(\d{4}\),\s+(\d+)-(\d+)\.$'


# Test it
citation = "Patricia S. Abril and Robert Plant. 2007. The patent holder's dilemma: Buy, sell, or troll? Commun. ACM 50, 1 (Jan. 2007), 36-44. https://doi.org/10.1145/1188913.1188915"

entry = "Ahsan Ahmad, Aftab Tariq, Hafiz Khawar Hussain, and Ahmad Yousaf Gill. 2023. Revolutionizing Healthcare: How Deep Learning is poised to Change the Landscape of Medical Diagnosis and Treatment. Journal of Computer Networks, Architecture and High Performance Computing 5, 2 (2023), 458–471. https://doi.org/10.1145/1188913.1188915"
match = re.match(pattern, entry)

if match:
    authors = match.group(1)
    year = match.group(2)
    title = match.group(3)
    journal = match.group(4)
    volume = match.group(5)
    issue = match.group(6)
    month = match.group(7)
    page_start = match.group(8)
    page_end = match.group(9)
    doi = match.group(10)
    # print(type(title))
    print(f"Authors: {authors}")
    print(f"Year: {year}")
    print(f"Title: {title}")
    print(f"Journal: {journal}")
    print(f"Volume: {volume}, Issue: {issue}")
    print(f"Pages: {page_start}-{page_end}")
    print(f"DOI: {doi}")
