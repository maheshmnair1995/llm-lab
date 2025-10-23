import streamlit as st
import requests

st.set_page_config(page_title="Meeting Notes Extractor", layout="centered")
st.title("🎙️ Meeting Notes Extractor")

st.markdown("Upload your meeting recording to extract structured notes and action items.")

uploaded_file = st.file_uploader("Upload Audio File", type=["wav", "mp3", "m4a", "ogg"])

if uploaded_file is not None:
    st.audio(uploaded_file)

    if st.button("Process Audio"):
        with st.spinner("Processing... Please wait ~1-2 minutes"):
            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            try:
                response = requests.post("http://localhost:8000/transcribe/", files=files, timeout=300)
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to backend: {e}")
            else:
                if response.ok:
                    data = response.json()
                    st.success("✅ Processing complete!")

                    st.subheader("📝 Summary")
                    st.write(data.get("structured_data", {}).get("summary", "No summary available."))

                    st.subheader("✅ Action Items")
                    for i, ai in enumerate(data.get("structured_data", {}).get("action_items", []), 1):
                        st.markdown(f"**{i}. {ai}**")

                    st.subheader("📄 Transcript")
                    st.text_area("Full Transcript", value=data.get("transcription", ""), height=300)
                else:
                    st.error(f"Processing failed: {response.text}")
