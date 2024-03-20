### evaluation script
import pandas as pd
import re

class Evaluator:
    def __init__(self):
        self.base_gnomad = pd.read_csv(r"C:\Shreya_files\Llama-2-GGML-Medical-Chatbot\data\teste.csv")
        self.base_links = self.base_gnomad['Link'].tolist()
        self.base_title = self.base_gnomad['Title'].tolist()

    def evaluate(self, source_documents):
        gnomad = 0
     
        for i in source_documents:
            try:
                if i.metadata['reference_links']:
                    ref_links = i.metadata['reference_links'].split(",")
                    ref_links = [re.sub(r"https?://", "", link) for link in ref_links]
                    self.base_links = [re.sub(r"https?://", "", link) for link in self.base_links]
                    title = i.metadata['title'].split(",")

                    for link in self.base_links:
                        for ref_link in ref_links:
                            if link in ref_link:
                                gnomad = gnomad + 1
            except:
                print(i)

        return gnomad