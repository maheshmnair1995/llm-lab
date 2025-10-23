from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
import tempfile
import uvicorn
import json
from pathlib import Path
import re

app = FastAPI()

# Allow frontend (Streamlit) to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Whisper model
model = WhisperModel("small", device="cpu", compute_type="int8")

@app.post("/transcribe/")
async def transcribe(file: UploadFile):
    # Save temp audio file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    segments, _ = model.transcribe(tmp_path)
    transcription = " ".join([segment.text for segment in segments])

    # Extract tasks/action items
    structured_data = extract_action_items(transcription)

    # Cleanup
    Path(tmp_path).unlink(missing_ok=True)
    return {"transcription": transcription, "structured_data": structured_data}

def extract_action_items(text: str):
    """
    Simple heuristic action-item extractor using regex and keyword spotting.
    You can enhance this with LLM or few-shot prompt-based models later.
    """
    sentences = re.split(r'[.!?]\s+', text)
    action_items = [s for s in sentences if any(word in s.lower() for word in ["need to", "should", "action", "plan", "follow up", "todo"])]
    
    return {
        "summary": text[:400] + "...",
        "action_items": action_items
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
