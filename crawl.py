import json
from selenium import webdriver
from bs4 import BeautifulSoup

PATH = 'C:\Program Files (x86)\chromedriver.exe'


def get_dict_value(dictionary, key):
    '''
        Given dictionary and key, return corresponding value. If key not found, return None.
    '''
    if key not in dictionary:
        return None
    else:
        return dictionary[key]


# url to website for crawl
url = 'https://www.nationalcrimeagency.gov.uk/most-wanted-search'

# dictionary of information from crawl
info_dict = {}

# list from people search
people_list = []

# prepopulate dictionary
info_dict['source_code'] = 'UK_MWL'
info_dict['source_name'] = 'UK Most Wanted List'
info_dict['source_url'] = url

# start driver
driver = webdriver.Chrome(PATH)

# go to url and parse
driver.get(url)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

info_dict['source_title'] = driver.title

# find element on main page that contains person info
all_people = driver.find_elements_by_class_name(
    'span4')

# list of links to crawl
link_list = []

# find all the links to indiviudal persons
for person in all_people:
    link = person.find_element_by_tag_name('a')
    link_list.append(link.get_attribute('href'))

# go to each link and gather info
for link in link_list:
    # go to each link
    driver.get(link)

    # parse current page
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # get full name of person
    full_name = soup.find('h2', {'itemprop': 'headline'}).text.strip().split()

    first_name = full_name[0].upper()
    last_name = full_name[1].upper()

    # get background information of incident
    background = soup.find(
        'div', {'itemprop': 'articleBody'}).find('p').text.strip()

    # create dictionary for all personal info that is found on the page
    personal_info = {}

    # populate dictionary
    for tag in soup.find_all('span', class_='field-label'):
        personal_info[tag.text.strip().lower().replace(
            ':', '')] = tag.find_next_sibling('span').text

    # create instance of person
    person = {
        'firstname': first_name,
        'lastname': last_name,
        'about': {
            'age': get_dict_value(personal_info, 'age range'),
            'gender': get_dict_value(personal_info, 'sex'),
            'height': get_dict_value(personal_info, 'height'),
            'build': get_dict_value(personal_info, 'build'),
            'hair_color': get_dict_value(personal_info, 'hair colour'),
            'hair_length': get_dict_value(personal_info, 'hair length'),
            'ethnic_appearance': get_dict_value(personal_info, 'ethnic appearance'),
        },
        'other': {
            'background_information': background,
            'location_of_crime': get_dict_value(personal_info, 'location'),
            'date_of_incident': get_dict_value(personal_info, 'date of incident'),
            'type_of_crime': get_dict_value(personal_info, 'crime'),
            'additional_information': get_dict_value(personal_info, 'additional information'),
            'related_information': get_dict_value(personal_info, 'related information')
        }
    }

    # add person to the persons list
    people_list.append(person)

# quit driver
driver.quit()

# add the list of people found to the dictionary of crawled information
info_dict['persons'] = people_list

# create json file for crawled information
with open('results.json', 'w') as f:
    json.dump(info_dict, f)
