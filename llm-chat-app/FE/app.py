import streamlit as st
import requests

st.title("My AI Chat Assistant")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat input (Enter to send)
user_input = st.chat_input("Type your message here...")

# If user sends message
if user_input:
    # Add user message
    st.session_state.messages.append(("You", user_input))

    # Call backend
    try:
        response = requests.post("http://localhost:8000/chat", json={"prompt": user_input})
        if response.status_code == 200 and response.headers.get("Content-Type", "").startswith("application/json"):
            response_json = response.json()
            answer = response_json.get("message", {}).get("content", "")
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            answer = ""
    except Exception as e:
        st.error(f"Request failed: {e}")
        answer = ""

    # Add LLM response
    st.session_state.messages.append(("LLM", answer))

# Display messages
for sender, msg in st.session_state.messages:
    with st.chat_message(sender.lower() if sender in ["You", "LLM"] else "user"):
        st.markdown(msg)
