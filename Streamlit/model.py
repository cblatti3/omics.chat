#import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import CTransformers
from langchain.chains import RetrievalQA
import json
from langchain.memory import ChatMessageHistory
from langchain.memory import ConversationBufferMemory


DB_FAISS_PATH =  r'vectorstores/db_faiss_mc'

custom_prompt_template = """Use the following pieces of information to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context: {context}
Question: {question}

Only return the helpful answer below and nothing else.
Helpful answer:
"""

def set_custom_prompt():
    prompt = PromptTemplate(template=custom_prompt_template,
                            input_variables=['context', 'question'])
    return prompt

def create_history():
    qna = json.load(open('qa.json', 'r', encoding="utf8"))
    history = ChatMessageHistory()
    for q in qna:
        history.add_ai_message(q['question'])
        history.add_user_message(q['answer'])

def create_conversation_buffer():
    memory = ConversationBufferMemory()
    memory.save_context({"input": "hi"}, {"output": "whats up"})


def retrieval_qa_chain(llm, prompt, db): 
    chat_history = create_history()
    print(chat_history)
    qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                           chain_type='stuff',
                                           memory = chat_history,
                                           retriever=db.as_retriever(search_kwargs={'k': 2}),
                                           return_source_documents=True,
                                           chain_type_kwargs={'prompt': prompt}
                                           )
    return qa_chain

def load_llm():
    llm = CTransformers(
        model="TheBloke/Llama-2-7B-Chat-GGML",
        model_type="llama",
        max_new_tokens=512,
        temperature=0.5
    )
    return llm

def qa_bot():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'})
    db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization = True)
    llm = load_llm()
    return llm, db

def qa_bot_query(query, llm, db):

    qa_prompt = set_custom_prompt()
    qa = retrieval_qa_chain(llm, qa_prompt, db)
    answer = qa({'query': query})
    return answer['result']

def qa_bot_conversation(answer):
    conversation = []
    conversation.append({"role": "bot", "message": answer})
    return conversation

def main():
    llm, db = qa_bot()
    print("Type 'exit' to exit the chatbot or type anything else to continue the conversation")
    conv_control = ''
    while conv_control!= "exit":
        query = input("Ask your question here:")
        answer = qa_bot_query(query, llm, db)
        final_response = qa_bot_conversation(answer)
        print(final_response)
        conv_control = input("Type 'exit' to exit the chatbot or type anything else to continue the conversation: ")
        conv_control = conv_control.lower().strip()
    print("Goodbye!")
    

if __name__ == "__main__":
    main()
