import streamlit as st
import requests

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

# --- Initialize session state ---
if "history" not in st.session_state:
    st.session_state.history = []
if "current_answer" not in st.session_state:
    st.session_state.current_answer = ""

# --- Sidebar: Document Ingest ---
st.sidebar.title("📂 Document Ingestion")
uploaded_files = st.sidebar.file_uploader(
    "Upload documents (TXT, PDF, DOCX)", type=["txt", "pdf", "docx"], accept_multiple_files=True
)

if st.sidebar.button("Ingest"):
    if uploaded_files:
        for f in uploaded_files:
            files = {"file": (f.name, f.getvalue())}
            data = {"source_name": f.name}
            resp = requests.post(f"{BACKEND_URL}/ingest", files=files, data=data)
            if resp.status_code == 200:
                st.sidebar.success(f"Ingested {f.name}")
            else:
                st.sidebar.error(f"Failed to ingest {f.name}")
    else:
        st.sidebar.warning("Please upload at least one file.")

# --- Main Area: Q&A ---
st.title("Custom Chatbot Q&A 💬")
st.markdown("Ask questions based on your uploaded documents.")

# --- Q&A Form ---
with st.form("ask_form", clear_on_submit=True):
    query = st.text_input("Type your question below:", key="query_input")
    submitted = st.form_submit_button("Ask")

    if submitted and query.strip():
        try:
            resp = requests.post(f"{BACKEND_URL}/query", json={"query": query})
            if resp.status_code == 200:
                answer = resp.json().get("answer", "")
                if answer:
                    # Capitalize first letter
                    answer = answer[0].upper() + answer[1:]
                    st.session_state.current_answer = answer
                    st.session_state.history.append({"question": query, "answer": answer})
                else:
                    st.warning("No relevant answer found.")
            else:
                st.error("Error fetching answer from backend.")
        except Exception as e:
            st.error(f"Exception: {str(e)}")

# --- Display Current Q&A ---
if st.session_state.current_answer:
    st.markdown("### 🧠 Current Q&A")
    st.markdown(f"**Q:** {st.session_state.history[-1]['question']}")
    st.markdown(f"**A:** {st.session_state.current_answer}")
    st.markdown("---")

# --- Clear History Button ---
if st.button("Clear History"):
    st.session_state.history = []
    st.session_state.current_answer = ""

# --- Display Previous Q&A ---
if len(st.session_state.history) > 1:
    st.markdown("### 🕘 Previous Questions & Answers")
    # Skip the last one (current)
    for i, qa in enumerate(reversed(st.session_state.history[:-1]), 1):
        st.markdown(f"**Q{i}:** {qa['question']}")
        st.markdown(f"**A{i}:** {qa['answer']}")
        st.markdown("---")
