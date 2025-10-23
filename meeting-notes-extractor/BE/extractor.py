from llama_cpp import Llama
import json, re

# Load local quantized model (ggml)
llm = Llama(model_path="models/ggml-model-q4_0.bin")

PROMPT = """
You are an assistant that extracts structured meeting notes from transcripts.
Return JSON with keys: summary, decisions, action_items (list), follow_ups.
Each action item must have: task, owner, due, priority, context.
Transcript:\n{transcript}\n
JSON:
"""


def extract_artifacts(transcript: str):
    prompt = PROMPT.format(transcript=transcript[:40000])
    result = llm.create(prompt=prompt, max_tokens=512, temperature=0)
    output = result["choices"][0]["text"] if "choices" in result else result["text"]

    # Try parse JSON
    try:
        data = json.loads(output)
    except Exception:
        match = re.search(r"\{.*\}", output, re.S)
        data = json.loads(match.group(0)) if match else {
            "summary": "", "decisions": [], "action_items": [], "follow_ups": []
        }

    data['transcript'] = transcript
    return data
