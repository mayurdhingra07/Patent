import os
import re
import openai
import streamlit as st
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter

os.environ["OPENAI_API_KEY"] = "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"

# Function to extract sections from the text
def extract_sections(text):
    sections = {
        "title": "",
        "abstract": "",
        "background": "",
        "summary": "",
        "description": "",
        "claims": ""
    }

    sections["title"] = re.search(r"(?<=Title:)(.*?)(?=Abstract:)", text, re.DOTALL).group().strip()
    sections["abstract"] = re.search(r"(?<=Abstract:)(.*?)(?=Background:)", text, re.DOTALL).group().strip()
    sections["background"] = re.search(r"(?<=Background:)(.*?)(?=Summary:)", text, re.DOTALL).group().strip()
    sections["summary"] = re.search(r"(?<=Summary:)(.*?)(?=Detailed Description:)", text, re.DOTALL).group().strip()
    sections["description"] = re.search(r"(?<=Detailed Description:)(.*?)(?=Claims:)", text, re.DOTALL).group().strip()
    sections["claims"] = re.search(r"(?<=Claims:)(.*)", text, re.DOTALL).group().strip()

    return sections

# Function to get GPT-3 response
def get_gpt3_response(prompt, max_tokens=100):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response.choices[0].text.strip()

st.title("AI Patent Assistant")

uploaded_file = st.file_uploader("Upload a patent PDF", type=["pdf"])

if uploaded_file is not None:
    with open("uploaded_patent.pdf", "wb") as f:
        f.write(uploaded_file.getvalue())

    loader = UnstructuredFileLoader("uploaded_patent.pdf", mode="elements")
    document = loader.load()
    sections = extract_sections(" ".join([doc.text for doc in document]))
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

    # Task 1: Summarize the background
    background_summary_prompt = f"Summarize the following patent background in 100 words or less: {sections['background']}"
    background_summary = get_gpt3_response(background_summary_prompt, max_tokens=100)

    # Task 2: Explain the first claim with relevant text from the summary or description
    first_claim = sections["claims"].split("\n")[0].strip()
    claim_explanation_prompt = (
        f"Explain the first claim of the patent '{first_claim}' in 100 words or less, "
        f"with reference to the patent summary or detailed description: {sections['summary']} {sections['description']}"
    )
    first_claim_explanation = get_gpt3_response(claim_explanation_prompt, max_tokens=100)

    # Display the results of tasks 1 and 2
    st.write("Background summary:", background_summary)
    st.write("First claim explanation:", first_claim_explanation)

    # Task 3: Prompt user to input a target company or standard
    target = st.text_input("Enter a target company or standard")

    if target:
        # Task 4: Run GPT-3 query
        query = f"Does {target} provide a similar technology as the patent claim: {first_claim}?"
        gpt3_response = get_gpt3_response(query, max_tokens=100)

        # Display the result of Task 4
        st.write("GPT-3 response:", gpt3_response)
