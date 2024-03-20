from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import random
import json
import re
import pandas as pd

class GetResearchText:
    def __init__(self, link):
        self.link = link
        self.content = {}
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        with webdriver.Chrome(options=options) as driver:
            driver.get(self.link)
            time.sleep(random.randint(5, 10))  # Wait for page to load
            self.html = driver.page_source

        self.soup = BeautifulSoup(self.html, 'html.parser')
        driver.quit()

    def get_all_references(self):
        header_in_page = self.soup.find_all('h2')
        ref_tag = [j for j in header_in_page if "references" in j.get_text(strip=True).lower()]
        print(ref_tag)

        for j in ref_tag[0].find_next_siblings():
            
            text_journal = []
            journal_link = []
            text_of_ref = []

            print(j.name)
            tags = j.find_all('div')
            for tag in tags:
                tag_links = tag.find_all('a')
                for link in tag_links:
                    if "pubmed" in link.get_text(strip=True).lower():
                        text_journal.append(link.get_text(strip=True))
                        journal_link.append(link.get('href'))
                    else:
                        text_journal.append(link.get_text(strip=True))
                        journal_link.append(link.get('href'))
                        break
            
            journal_text = j.find_all('span', class_="element-citation")
            for journal in journal_text: 
                text_of_ref.append(journal.get_text(strip=True))           

        return text_journal, journal_link, text_of_ref
    
    def give_titles(self, ref_text):
        final_title = []
        for i in ref_text:
            title_to_link = '' 
            try:
                ref_title = i.split("et al")[1].strip()
                if 'doi' in ref_title.lower():
                    if ref_title.split("doi")[0].strip():
                        title_to_link = ref_title.split("doi")[0].strip()
                
                if title_to_link == '':
                    ### generate exception
                    raise Exception("Title not found")
            except Exception as e:
                try:
                    pattern = re.compile(r"\.\s(.*?)\.\d{4};")
                    match = pattern.search(i.strip())

                    if match:
                        title = match.group(1)
                        if len(title.split(" ")) > 4:
                            title_to_link = title

                    if title_to_link == '':
                        ### generate exception
                        raise Exception("Title not found")

                except Exception as e:
                    title_to_link = i.strip()

            title_to_link = re.sub(r"\.\s+", "", title_to_link)

            if title_to_link == '':
                title_to_link = i

            final_title.append(title_to_link)
        
        return final_title


    def get_data(self):
        
        # This code worked well for the pubmed central articles. It gets the content not sepaeated by headings
        head_in_page = self.soup.find_all('h2')
        paper_heading = self.soup.find_all('h1')
        title = paper_heading[0].get_text(strip=True)

        text_journal, journal_link, text_of_ref = self.get_all_references()
        print(len(text_journal), len(journal_link), len(text_of_ref))
        
        for j in head_in_page:
            all_text = ""
            all_links_a = []
            links = []
            text_ref = []
            for sibling in j.find_next_siblings():
                if sibling.name == 'div' or sibling.name == 'p' or sibling.name == 'h3' or sibling.name == 'h4' or sibling.name == 'h5' or sibling.name == 'h6':
                    all_text = all_text + sibling.get_text(strip=True)
                    all_links_a.extend(sibling.find_all('a'))


            if all_links_a:
                for link in all_links_a:
                    text_no = link.get_text(strip=True)
                    try:
                        links.append(text_no + " " + journal_link[int(text_no)-1])
                        text_ref.append(text_no + " " + text_of_ref[int(text_no)-1])
                    except:
                        pass
                    
            para_header = j.get_text(strip=True)
            para_header = re.sub(r'[^a-zA-Z\s]+', '', para_header).lower().strip()
            self.content[para_header] = para_header + "   " + all_text
            self.content['title'] = title
            self.content['url'] = self.link
            links = ", ".join(links)
            self.content['reference_links'+ "__" + para_header] = links
            titles_to_links = self.give_titles(text_ref)
            titles_to_links = ", ".join(titles_to_links)
            self.content['reference'+ "__" + para_header] = titles_to_links

        return self.content


def main():
    disease_file = pd.read_csv(r'C:\Shreya_files\Llama-2-GGML-Medical-Chatbot\data\papers_that_cite_gnomad.csv', index_col=0)
    disease_to_search = "heart failure"

    url_required = []

    def point_titles(x):
        if re.search(disease_to_search.lower().strip(), x['Title'].lower().strip()):
            if x['URL'].startswith("http"):
                url_required.append(x['URL'])

    def generate_links():
        disease_file.apply(lambda x: point_titles(x), axis = 1)


    all_papers = []
    generate_links()

    url_required = ["https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10811556",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10556087",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10371173",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9302582",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10773142",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8611834",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6523007",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6332775",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5322656",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10581410",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10607512"]

    for i in range(len(url_required) - 1, len(url_required)):
        print(i)
        research_text = GetResearchText(url_required[i])
        data = research_text.get_data()
        data['disease'] = disease_to_search
        all_papers.append(data)
        
    #Output:
    filename = r'C:\Shreya_files\Llama-2-GGML-Medical-Chatbot\data\research_text_pubmed.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_papers, f, ensure_ascii=False, indent=4, sort_keys=False, default=str)


if __name__ == "__main__":
    main()
