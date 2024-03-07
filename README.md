We are here creating a medical chatbot that assists with research in genetics.

##### The source code has been taken from this git repo:
[text](https://github.com/ThisIs-Developer/Llama-2-GGML-Medical-Chatbot)

#### Changes Introduced:
1. Rather than referencing to medical encyclopedia the code now uses gnomad help articles to answer question.
2. The langchain gathers context from QnA from the help page
3. The sources mentioned in 1 and 2 have been scraped from gnomad official website and the code for the same is available in the scrape folder
4. Removed streamlit. The application can be started using the command 'python Streamlit\model.py'
5. Example chat screenshot is available in the "conversation_sample" folder