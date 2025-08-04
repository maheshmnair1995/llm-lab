import streamlit as st
from transformers import pipeline
import sys
import os

# Add parent directory (document-summarizer) to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from BE.utils.pdf_utils import extract_text_from_pdf

# Load summarizer
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

summarizer = load_summarizer()

# UI
st.title("📄 Document Summarization Tool")

uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")

if uploaded_file:
    with st.spinner("Extracting text from PDF..."):
        full_text = extract_text_from_pdf(uploaded_file)
    
    st.subheader("Extracted Text (preview)")
    st.text_area("Text", value=full_text[:3000], height=200)

    if st.button("Summarize"):
        with st.spinner("Summarizing..."):
            # Limit to first 1000 chars to stay within model limits
            summary = summarizer(full_text[:1000], max_length=150, min_length=40, do_sample=False)[0]['summary_text']
        st.subheader("🧠 Summary")
        st.success(summary)
