import os
import logging
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator
from groq import Groq

# ---------- 1. CONFIG (was config.py) ----------
AI_API_KEY = os.environ.get("AI_API_KEY", "")
AI_MODEL = os.environ.get("AI_MODEL", "llama-3.3-70b-versatile")
PORT = int(os.environ.get("PORT", 8000))

# ---------- 2. AI PROMPTS + CLIENT (was ai_service.py) ----------
client = Groq(api_key=AI_API_KEY)

BASE_RULES = """Rules:
- Preserve the original meaning.
- Do not add or remove information.
- Return only the resulting text, no explanations."""

MODE_PROMPTS = {
    "grammar": f"You are an AI writing assistant. Correct grammar, spelling, punctuation, and minor clarity issues only. Preserve tone.\n{BASE_RULES}",
    "paraphrase": f"You are an AI writing assistant. Rewrite the text using different wording while preserving meaning.\n{BASE_RULES}",
    "formal": f"You are an AI writing assistant. Rewrite the text in a professional, formal tone.\n{BASE_RULES}",
    "polite": f"You are an AI writing assistant. Rewrite the text to sound respectful and courteous.\n{BASE_RULES}",
    "friendly": f"You are an AI writing assistant. Rewrite the text to sound warm and approachable.\n{BASE_RULES}",
    "concise": f"You are an AI writing assistant. Reduce unnecessary words while preserving meaning.\n{BASE_RULES}",
}

class AIServiceError(Exception):
    pass

def improve_text(text: str, mode: str) -> str:
    system_prompt = MODE_PROMPTS.get(mode, MODE_PROMPTS["grammar"])
    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise AIServiceError(str(e)) from e

# ---------- 3. REQUEST/RESPONSE SHAPES (was models.py) ----------
Mode = Literal["grammar", "paraphrase", "formal", "polite", "friendly", "concise"]

class ImproveRequest(BaseModel):
    text: str
    mode: Mode = "grammar"

    @field_validator("text")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text must not be empty")
        if len(v) > 2000:
            raise ValueError("text too long (max 2000 chars)")
        return v

class ImproveResponse(BaseModel):
    original_text: str
    mode: str
    improved_text: str

# ---------- 4. THE APP ITSELF (was main.py) ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-writing-assistant")

app = FastAPI(title="AI Writing Assistant")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("app/static/index.html")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/improve", response_model=ImproveResponse)
def improve(request: ImproveRequest):
    try:
        result = improve_text(request.text, request.mode)
    except AIServiceError as e:
        logger.error(f"AI service failed: {e}")
        raise HTTPException(status_code=502, detail="AI service unavailable, try again.")
    except Exception:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail="Something went wrong.")

    return {"original_text": request.text, "mode": request.mode, "improved_text": result}