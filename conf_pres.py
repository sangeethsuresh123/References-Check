# conference presentation

import re

pattern = r'^(.+?)\.\s+(\d{4})\.\s+(.+?)\.\s+Presentation at the\s+(.+?),\s+(.+?),\s+([A-Z]{2}),\s+([A-Z]{3})\.(?:\s*)(?:(https?://[^\s]+))?$'

# Test it with URL
citation1 = "Brian J. Reiser. 2014. Designing coherent storylines aligned with NGSS for the K-12 classroom. Presentation at the National Science Education Leadership Association Meeting, Boston, MA, USA.https://www.academia.edu/6884962/Designing_Coherent_Storylines_Aligned_with_NGSS_for_the_K_12_Classroom"

# Test it without URL
citation2 = "Brian J. Reiser. 2014. Designing coherent storylines aligned with NGSS for the K-12 classroom. Presentation at the National Science Education Leadership Association Meeting, Boston, MA, USA."

match1 = re.match(pattern, citation1)
match2 = re.match(pattern, citation2)


def print_match(match):
    if match:
        authors = match.group(1)
        year = match.group(2)
        title = match.group(3)
        event = match.group(4)
        city = match.group(5)
        state = match.group(6)
        country = match.group(7)
        url = match.group(8) if match.group(8) else "Not provided"

        print(f"Authors: {authors}")
        print(f"Year: {year}")
        print(f"Title: {title}")
        print(f"Event: {event}")
        print(f"City: {city}")
        print(f"State: {state}")
        print(f"Country: {country}")
        print(f"URL: {url}")
    else:
        print("No match found")


print("With URL:")
print_match(match1)
print("\nWithout URL:")
print_match(match2)
