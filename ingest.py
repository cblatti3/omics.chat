from langchain.text_splitter import RecursiveJsonSplitter
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.docstore.document import Document


DATA_PATH=["data/articles.json", "data/gnomad_help.json"]
DATA_PATH_PDF=[r"C:\Shreya_files\Llama-2-GGML-Medical-Chatbot\data\research_text_pubmed.json"]
DB_FAISS_PATH="vectorstores/db_faiss_mc_1"

def load_documents():
    ## loan json files from data folder
    documents = []
    for path in DATA_PATH:
        with open(path, 'r', encoding="utf8") as file:
            text = json.load(file)

            for articles in text:
                doc = Document(page_content = articles['text'], metadata={"source": articles["link"], "title": articles["title"]})
                documents.append(doc)

    return documents

def load_paper():
    ## load pdf files from data folder
    documents = []
    for path in DATA_PATH_PDF:
        with open(path, 'r', encoding="utf8") as file:
            text = json.load(file)

    for paper in text:
       
        for key in paper.keys():
            if len(paper[key].split(" ")) < 10 or key == "disease" or key == "title" or key == "reference" or "reference" in key or "url" in key or "title" in key:
                continue
            try:
                doc = Document(page_content = paper[key], metadata={"disease": paper["disease"], "title": paper["title"], "reference": paper["reference"+ "__" + key], "reference_links": paper["reference_links" + "__" + key]})

            except:
                try:
                    doc = Document(page_content = paper[key], metadata={"disease": paper["disease"], "title": paper["title"], "reference": '', "reference_links": ''})
                except Exception as e:
                    print(e)
                    print(paper[key])
                    continue
            documents.append(doc)

    return documents


def create_vector_db(documents):
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300)

    split_docs = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs = {'device': 'cpu'})

    db = FAISS.from_documents(split_docs, embeddings)
    db.save_local(DB_FAISS_PATH)

if __name__ == "__main__":
    documents = load_documents()
    paper_docs = load_paper()
    documents.extend(paper_docs)
    create_vector_db(documents)
    

