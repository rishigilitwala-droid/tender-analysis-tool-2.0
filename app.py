import streamlit as st
import pdfplumber
import docx
import pandas as pd
from gpt4all import GPT4All

# Load local AI model
model = GPT4All("mistral")

def extract_text(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        with pdfplumber.open(uploaded_file) as pdf:
            return " ".join(page.extract_text() for page in pdf.pages if page.extract_text())
    elif uploaded_file.name.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        return " ".join(p.text for p in doc.paragraphs)
    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
        return df.to_string()
    else:
        return "Unsupported file format"

def analyze_text(text, detail_level, style, fields):
    prompt = f"""
    Summarize this tender/procurement document into structured HTML cards.
    Style: {style}
    Detail level: {detail_level}
    Include fields: {", ".join(fields)}
    Output only valid HTML.
    Document text:
    {text}
    """
    return model.generate(prompt, max_tokens=1200)

# Streamlit UI
st.title("📑 Tender Analysis Tool")
st.write("Upload a PDF, Word, or Excel tender document to generate summary cards.")

uploaded_file = st.file_uploader("Upload file", type=["pdf", "docx", "xlsx"])

# --- Customization Section ---
st.sidebar.header("⚙️ Customize Summary Cards")
detail_level = st.sidebar.selectbox("Detail Level", ["Brief", "Moderate", "Detailed"])
style = st.sidebar.selectbox("Card Style", ["Bootstrap", "Tailwind", "Minimal HTML"])
fields = st.sidebar.multiselect(
    "Fields to Include",
    ["Project Name", "Issuing Authority", "Scope", "Deadlines", "Financials", "Submission Process", "Contact Info"],
    default=["Project Name", "Issuing Authority", "Deadlines"]
)

if uploaded_file:
    text = extract_text(uploaded_file)
    st.success("File uploaded and text extracted!")
    
    if st.button("Analyze Document"):
        with st.spinner("Analyzing with AI..."):
            html_output = analyze_text(text, detail_level, style, fields)
        st.markdown(html_output, unsafe_allow_html=True)
