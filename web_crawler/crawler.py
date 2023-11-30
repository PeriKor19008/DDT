import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

def get_education(url):
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')

    info_box = soup.find('table', class_='infobox biography vcard')
    if info_box:
        alma_mater_label = info_box.find('th', class_="infobox-label",  string='Alma\xa0mater')
        
        if alma_mater_label:
            info_box_data = alma_mater_label.find_next()
            alma_mater_row = info_box_data.find_all('a')
            alma_mater_data = [link.get_text(strip=True) for link in alma_mater_row]

            info_box_awards = get_awards(info_box)

            return alma_mater_data, info_box_awards
           
    education_div = soup.find('div', id='mw-normal-catlinks')
    if education_div:
        ul_element = education_div.find('ul')
        if ul_element:
            alumni_titles = [li.get_text(strip=True).replace('alumni', '') for li in ul_element.find_all('li') if 'alumni' in li.get_text().lower()]
            info_box_awards = get_awards(info_box)

            return alumni_titles, info_box_awards
                
    return None, None

def get_awards(awards):

    if awards:
        awards_label = awards.find('th', class_="infobox-label",  string='Awards')
        if awards_label:
            info_box_data = awards_label.find_next()
            awards_row = info_box_data.find_all('a')
            awards_data = [link.get_text(strip=True) for link in awards_row]

            return awards_data
    
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
for li in li_elements[670:-13]:  
    person_data = {}
    first_a_tag = li.find('a', href=True)
    if first_a_tag:
        person_data['Name'] = first_a_tag.get('title')
        
        person_url = 'https://en.wikipedia.org' + first_a_tag['href']
        print(f"Checking URL for {person_data['Name']}: {person_url}")
        
        person_data['Education'], person_data['Awards'] = get_education(person_url)

        data.append(person_data)

df = pd.DataFrame(data)
df['Name'] = df['Name'].apply(remove_parentheses)
df.to_csv('web_crawler/computer_scientists.csv', index=False)