import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

def get_education_from_page(url):
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')

    info_box = soup.find('table', class_='infobox biography vcard')
    if info_box:
        alma_mater_label = info_box.find('th', class_="infobox-label",  string='Alma\xa0mater')
        if alma_mater_label:
            info_box_data = alma_mater_label.find_next()
            final = info_box_data.find_all('a')
            names = [link.get_text(strip=True) for link in final]

            return names
           
    education_div = soup.find('div', id='mw-normal-catlinks')
    if education_div:
        ul_element = education_div.find('ul')
        if ul_element:
            alumni_titles = [li.get_text(strip=True).replace('alumni', '') for li in ul_element.find_all('li') if 'alumni' in li.get_text().lower()]
            return alumni_titles
                
    return None

def remove_parentheses(title):
    return re.sub(r'\([^)]*\)', '', title)

url = "https://en.wikipedia.org/wiki/List_of_computer_scientists"

response = requests.get(url)
html_content = response.content
soup = BeautifulSoup(html_content, 'html.parser')

specific_div = soup.find('div', class_='mw-content-ltr mw-parser-output')
li_elements = specific_div.find_all('li')

data = []
for li in li_elements[:-13]:  
    person_data = {}
    first_a_tag = li.find('a', href=True)
    if first_a_tag:
        person_data['Name'] = first_a_tag.get('title')
        
        person_url = 'https://en.wikipedia.org' + first_a_tag['href']
        print(f"Checking URL for {person_data['Name']}: {person_url}")
        
        person_data['Education'] = get_education_from_page(person_url)

        data.append(person_data)

df = pd.DataFrame(data)
df['Name'] = df['Name'].apply(remove_parentheses)
df.to_csv('web_crawler/computer_scientists.csv', index=False)
