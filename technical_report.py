# Technical Report:
import re

pattern = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+(.+?)\s+(Technical Report|TR)\s+([A-Z]+-\d+)\.\s+(.+?),\s+(.+?),\s+([A-Z]{2})\.$'

# Test it
citation = "David Harel. 1978. LOGICS of Programs: AXIOMATICS and DESCRIPTIVE POWER. MIT Research Lab Technical Report TR-200. Massachusetts Institute of Technology, Cambridge, MA."

match = re.match(pattern, citation)

if match:
    authors = match.group(1)
    year = match.group(2)
    title = match.group(3)
    institution_dept = match.group(4)
    report_type = match.group(5)
    report_number = match.group(6)
    institution = match.group(7)
    city = match.group(8)
    state = match.group(9)

    print(f"Authors: {authors}")
    print(f"Year: {year}")
    print(f"Title: {title}")
    print(f"Department: {institution_dept}")
    print(f"Report Type: {report_type}")
    print(f"Report Number: {report_number}")
    print(f"Institution: {institution}")
    print(f"City: {city}")
    print(f"State: {state}")
