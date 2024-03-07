from selenium import webdriver
from bs4 import BeautifulSoup
import time
import random
import json

# Initialize WebDriver
driver = webdriver.Chrome()
driver.get("https://gnomad.broadinstitute.org/help")
time.sleep(random.randint(5, 10))  # Wait for the page to load

# Parse the main help page
soup = BeautifulSoup(driver.page_source, 'html.parser')

def get_links_function(soup):
    articles = []
    article_list = soup.find('div', class_='sc-hMqMXs kuzRIz').find('div', class_='sc-iAyFgw gFQpaU').find('ul', class_='List-sc-4j87st-0 fQRmhM')
    if article_list:
        links = article_list.find_all('li')
        for li in links:
            a_tags = li.find_all('a')
            if a_tags:
                link_to_articles = a_tags[0]['href']
                title = a_tags[0].text
                articles.append({'title': title, 'link': 'https://gnomad.broadinstitute.org' + link_to_articles})
    return articles

def get_articles(articles):
    for article in articles:
        driver.get(article['link'])
        time.sleep(random.randint(1, 5))  # Wait for the page to load
        article_soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Assuming the article text is within a div with a class that needs to be updated according to actual page structure
        article_body = article_soup.find('div', class_='sc-kpOJdX frycJh')
        if article_body:
            article_text = article_body.get_text(separator="\n", strip=True)
            article['text'] = article_text
        else:
            article['text'] = "Could not find article body."

    driver.quit()  # Quit the driver after processing all articles
    return articles

articles = get_links_function(soup)
articles_with_text = get_articles(articles)

# Save to JSON
filename = 'gnomad_help.json'
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(articles_with_text, f, ensure_ascii=False, indent=4, sort_keys=False)

