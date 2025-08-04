import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    external_url = "http://localhost:11434/api/chat"
    
    payload = {
        "model": "llama2",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False  # This avoids multiline JSON issue
    }

    try:
        response = requests.post(external_url, json=payload)
        print("Raw response:", response.text)

        if response.status_code == 200:
            return response.json()
        else:
            return JSONResponse(
                status_code=response.status_code,
                content={"error": "Upstream error", "details": response.text}
            )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Request failed: {e}"}
        )
