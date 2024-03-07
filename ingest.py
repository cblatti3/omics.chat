from langchain.text_splitter import RecursiveJsonSplitter
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.docstore.document import Document


DATA_PATH=["data/articles.json", "data/gnomad_help.json"]
#DB_FAISS_PATH="vectorstores/db_faiss"
DB_FAISS_PATH="vectorstores/db_faiss_mc"

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



def create_vector_db(documents):
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500)

    #split_docs = [text_splitter.split_text(doc) for doc in documents]

    split_docs = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs = {'device': 'cpu'})

    db = FAISS.from_documents(split_docs, embeddings)
    db.save_local(DB_FAISS_PATH)

if __name__ == "__main__":
    documents = load_documents()
    print(documents)
    create_vector_db(documents)

