# article under review
import re

pattern = r'^(.+?)\s+\((\d{4})\)\.\s+(.+?)\.\s+Manuscript submitted for review\.$'

# Test it
citation = "R. Baggett, M. Simecek, C. Chambellan, K. Tsui, and M. Fraune (2023). Fluidity in the Phased Framework of Technology Acceptance: Case Study to Gain a Holistic Understanding of (Older Adult) Participant Advancement Through Acceptance Phases with Mobile Telepresence Robots. Manuscript submitted for review."

match = re.match(pattern, citation)

if match:
    authors = match.group(1)
    year = match.group(2)
    title = match.group(3)

    print(f"Authors: {authors}")
    print(f"Year: {year}")
    print(f"Title: {title}")
    print(f"Status: Manuscript submitted for review")
else:
    print("No match found")
