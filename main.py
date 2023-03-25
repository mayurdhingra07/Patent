import streamlit as st
from docquery import document, pipeline
import requests
from io import BytesIO

docquery_pipeline = pipeline('document-question-answering')

@st.cache
def load_document_from_url(url):
    response = requests.get(url)
    return document.load_document(BytesIO(response.content))

st.title("Memory Standards Document Query")

pdf_urls = []
for i in range(14):
    pdf_url = st.text_input(f"PDF {i+1} URL:")
    if pdf_url:
        pdf_urls.append(pdf_url)

question = st.text_input("Enter your question:")

if st.button("Ask") and question and pdf_urls:
    results = []
    for url in pdf_urls:
        doc = load_document_from_url(url)
        result = docquery_pipeline(question=question, **doc.context)
        results.append((url, result["answer"]))

    st.write("Results:")
    for url, answer in results:
        st.write(f"From {url}:")
        st.write(answer)
