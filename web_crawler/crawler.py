import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import numpy as np

url = "https://en.wikipedia.org/wiki/List_of_computer_scientists"

response = requests.get(url)
html_content = response.content
soup = BeautifulSoup(html_content, 'html.parser')

specific_div = soup.find('div', class_='mw-content-ltr mw-parser-output')
li_elements = specific_div.find_all('li')

data = []
for li in li_elements:
    person_data = {}
    first_a_tag = li.find('a', href=True)
    if first_a_tag:
        person_data['Name'] = first_a_tag.get('title')
        data.append(person_data)

df = pd.DataFrame(data)
df = df.iloc[:-13]


def remove_parentheses(title):
    return re.sub(r'\([^)]*\)', '', title)


df['Name'] = df['Name'].apply(remove_parentheses)
df['Education'] = "PhD"
df['Awards'] = np.random.randint(0, 8, size=len(df))
df.to_csv('computer_scientists.csv', index=False)
