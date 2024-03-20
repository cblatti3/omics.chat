from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import requests
import random
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import datetime
from selenium.common.exceptions import NoSuchElementException
import json



driver = webdriver.Chrome()

driver.get("https://gnomad.broadinstitute.org/help")

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
sleep_time = random.randint(5, 10)
time.sleep(sleep_time) 
driver.quit()


QA_headers = []


def get_QA():
    #print(soup.get_text())
    h3_tags = soup.find_all('h3')
    all_answers = []
    serial = 0
    # Extract and print the text from each <h3> tag
    for h3 in h3_tags:
        a_tag = h3.find_all('a')
        if a_tag:
            for a in a_tag:
                
                QA_headers.append(a.get('id'))
                ul = h3.find_next('ul')

                if ul:
                    # Extract and print each <li> within the <ul>
                    for li in ul.find_all('li'):
                        serial = serial + 1
                        #print("Iterating through all descendants in an li:")
                        for descendant in li.descendants:
                            if descendant.name:  # This filters out NavigableString elements which are not tags
                                if descendant.descendants:
                                    for d in descendant.descendants:
                                        if d.name in ['table']:
                                            tab_data = []
                                            for row in descendant.find_all('tr'):
                                                row_data = [cell.get_text(strip=True) for cell in row.find_all(['th', 'td'])]
                                                print("    ", row_data)
                                                tab_data.append(row_data)
                                            all_answers[-1]['Table'] = tab_data

                                        if d.name in ['svg', 'audio', 'audio controls']:
                                            print(d.name)
                                            continue
                                            
                                                 
                                        if d.name in ['p', 'h4']:

                                            if '?' in d.get_text(strip=True):
                                                qa = d.get_text(strip=True)
                                                all_answers.append({'question': qa, 'serial': serial, 'answer': ''})
                                                

                                            else:
                                                #ans = ans + d.get_text(strip=True)
                                                all_answers[-1]['answer'] = all_answers[-1]['answer']+ d.get_text(strip=True)

    return all_answers

                                
def unique_dicts_by_key(dict_list, unique_key):
    """
    Returns a list of dictionaries, filtered to be unique by the specified key.
    """
    unique_values = set()
    unique_dicts = []

    for d in dict_list:
        if d[unique_key] not in unique_values:
            unique_values.add(d[unique_key])
            unique_dicts.append(d)

    return unique_dicts


ans = get_QA()

filename = 'qa.json'

# Writing JSON data
ans_unique = unique_dict_list = unique_dicts_by_key(ans, 'serial')

with open(filename, 'w', encoding='utf-8') as f:
    json.dump(ans_unique, f, ensure_ascii=False, indent=4, sort_keys=False, default=str)
