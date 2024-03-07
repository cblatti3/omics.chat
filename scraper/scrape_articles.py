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

driver.get("https://gnomad.broadinstitute.org/news/category/releases/")

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
sleep_time = random.randint(5, 10)
time.sleep(sleep_time)  

# try:
#     link = driver.find_element(By.LINK_TEXT, "Variant Co-occurrence Counts by Gene in gnomAD")
#     link.click()

    # page_source = link.page_source
    # soup = BeautifulSoup(page_source, 'html.parser')
    # all_text = soup.get_text()

    # Wait for the page to load after clicking
    #time.sleep(2)  # Adjust the sleep time as necessary

    # content_element = driver.find_element(By.CLASS_NAME, "article-body")
    # time.sleep(2)  # Adjust the sleep time as necessary
    # content_text = content_element.text

    # save text to a file
    # with open("gnomad.txt", "w", encoding='utf-8') as file:
    #     file.write(content_text)


# except NoSuchElementException:
#     print("The link was not found on the page.")

def get_articles(articles):
    for article in articles:
        # Fetch the article page
        response = requests.get(article['link'])
        article_soup = BeautifulSoup(response.content, 'html.parser')
        
        # Assuming the article text is within a <div> with class "article-body"
        # This will vary based on the website's structure
        article_body = article_soup.find('section', class_='article-body')
        
        if article_body:
            article_text = article_body.get_text(separator="\n", strip=True)
            # Add the scraped text to your article dictionary
            article['text'] = article_text
        else:
            article['text'] = "Could not find article body."
        
        # Be respectful to the server; add a short delay between requests
        sleep_time = random.randint(1, 5)
        time.sleep(sleep_time)

    return articles


def get_links_function():
    soup = BeautifulSoup(html, 'html.parser')
    driver.quit()
    articles = []

    # Assuming each article is in an 'article' tag, and the date is within a 'span' with class 'date'
    for article in soup.find_all('article'):
        date_str = article.find('div', class_='article-meta').find('span', class_='article-date').get_text()
        # Parse the date assuming it's in a format like "January 1, 2023"
        article_date = datetime.datetime.strptime(date_str, '%B %d, %Y').date()
        print(article_date)
        # Check if the date is within your range
        if datetime.date(2020, 10, 19) <= article_date <= datetime.date(2023, 3, 1):
            title = article.find('h2').get_text()  # Hypothetical structure
            link = article.find('a')['href']
            articles.append({'title': title, 'link': 'https://gnomad.broadinstitute.org' + link, 'date': article_date})

    return articles

articles = get_links_function()
text_body = get_articles(articles)

filename = 'articles.json'

# Writing JSON data
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(text_body, f, ensure_ascii=False, indent=4, sort_keys=False, default=str)
