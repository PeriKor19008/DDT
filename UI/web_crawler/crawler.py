import requests
import pandas as pd
from bs4 import BeautifulSoup
import re


def remove_parentheses(title):
    # Function to remove from names the parenthesis and its content e.g. Olaf Storaasli (computing)
    return re.sub(r'\([^)]*\)', '', title)


def clean_links(link):
    # Function to remove citation links because they are considered as a row in the data
    if link is not None:
        cleaned_links = [re.sub(r'\[\d+\]', '', links).replace(',', '').strip() for links in link]
        # Remove the empty strings
        cleaned_links = list(filter(None, cleaned_links))  
        
        return cleaned_links
    
    return None


def get_education(url):
    # Function that reads the website of each person
    # Takes argument a url link
    # Returns the Awards and Education
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    # Table on right side, which might contains alma mater and awards
    info_box = soup.find('table', class_='infobox biography vcard')
    if info_box:
        # Labels in the table are called infobox-label
        # Using the label we can find the next line in the html which is the class that contains information
        alma_mater_label = info_box.find('th', class_="infobox-label",  string='Alma\xa0mater')

        if alma_mater_label:
            info_box_data = alma_mater_label.find_next()
            alma_mater_row = info_box_data.find_all('a')
            alma_mater_data = [link.get_text(strip=True) for link in alma_mater_row]
            # Some scientists don't have data as a text but instead is the id the class
            if not alma_mater_data:
                alma_mater_data = [text.get_text(strip=True) for text in info_box_data]
            # Same principle, but using the Awards label
            mw_headline_awards = soup.find(class_='mw-headline', id=lambda x: x and 'awards' in x)
            awards = get_awards(info_box, mw_headline_awards)
            
            return alma_mater_data, awards
    # If the table doesn't exists we search for the container in the box of the website       
    education_div = soup.find('div', id='mw-normal-catlinks')
    if education_div:
        ul_element = education_div.find('ul')
        if ul_element:
            # In the container it might contain for example University of Patras alumni
            # We use the world alumni to find the Education of the person
            alumni_titles = [li.get_text(strip=True).replace('alumni', '') for li in ul_element.find_all('li') if 'alumni' in li.get_text().lower()]
            # Find class which contains "awards" in mw-headline, which is the main content
            mw_headline_awards = soup.find(class_='mw-headline', id=lambda x: x and 'awards' in x)
            awards = get_awards(info_box, mw_headline_awards)

            return alumni_titles, awards
                
    return [], 0


def get_awards(info_box_awards, mw_headline_awards):
    # Function to count the number of awards
    # Takes as arguments the data from soup.find
    # Returns the length of the array because we want the number of awards
    if info_box_awards:
        # If the table exists then we search for the Awards label
        # Same principle as the Alma Mater label
        awards_label = info_box_awards.find('th', class_="infobox-label",  string='Awards')
        if awards_label:
            info_box_data = awards_label.find_next()
            awards_row = info_box_data.find_all('a')
            awards_data = [link.get_text(strip=True) for link in awards_row]
            
            return len(clean_links(awards_data))

    if  mw_headline_awards:
        # If the table doesn't exists the we search for citation in the awards class
        # We use citations because for the people who have awards are always citated at the end
        # Also some don't have the awards as an ul/li but in a paragraph
        awards_citation = mw_headline_awards.find_all('sup')
        awards_data = [awards.get_text(strip=True) for awards in awards_citation]
       
        return len(clean_links(awards_data))

    return 0


def main():
    # Parse the html of the website
    url = "https://en.wikipedia.org/wiki/List_of_computer_scientists"
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')

    # All the names are in a specific class and each is in a list
    specific_div = soup.find('div', class_='mw-content-ltr mw-parser-output')
    li_elements = specific_div.find_all('li')

    data = []
    # Iterate all data except the last 13 which are not names
    for li in li_elements[:-13]:  
        person_data = {}
        # The names are placed in <a> tag
        first_a_tag = li.find('a', href=True)
        if first_a_tag:
            # Grab the text of <title> tag
            person_data['Name'] = first_a_tag.get('title')
            # Using the title, create a url for the person
            person_url = 'https://en.wikipedia.org' + first_a_tag['href']
            print(f"Checking URL for {person_data['Name']}: {person_url}")
            # Call function to get education and awards data
            person_data['Education'], person_data['Awards'] = get_education(person_url)

            data.append(person_data)

    df = pd.DataFrame(data)
    df['Name'] = df['Name'].apply(remove_parentheses)
    df['Education'] = df['Education'].apply(clean_links)
    df.to_csv('web_crawler/computer_scientists.csv', index=False)


if __name__ == "__main__":
    main()