# backend/main.py

from __future__ import annotations

from typing import Optional, Any
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI(title="DennisChat Backend", version="1.0.0")

# --- CORS: allow ANY origin (localhost + denarixx.com etc.) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Matrix X – OpenAI-style chat completions endpoint
MATRIX_COMPLETIONS_URL = "https://firebase-ai-models.matrixzat99.workers.dev/chat/completions"
MATRIX_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "You are DennisChat, the official AI assistant on the personal website "
    "of Dennis Charles (Denarixx).\n\n"
    "LANGUAGE RULES:\n"
    "- ALWAYS reply in the same language as the last user message.\n"
    "- If the user writes English, answer in English.\n"
    "- If the user writes German, answer in German.\n"
    "- If the user writes Spanish, answer in Spanish.\n"
    "- If the user writes Arabic, answer in Arabic.\n"
    "- If the user mixes languages, choose the language they use the MOST in that message.\n\n"
    "SCOPE:\n"
    "- You can talk about: Dennis’ background, mindset, skills, Denarixx projects, "
    "and the content visible on the site.\n"
    "- You may also answer *general, light* questions about AI, creativity, and careers "
    "– but keep them short and not too technical.\n\n"
    "CONTACT:\n"
    "- If the user asks for Dennis' contact or email, clearly give this: denarixx4@gmail.com\n"
    "- You may also mention that they can use the contact form on the site.\n\n"
    "SAFETY / PRIVACY:\n"
    "- Never reveal private technical details, schematics, exact business plans, or financial data.\n"
    "- Stay high-level. If the user pushes for deep internal details, say that these are private "
    "and only shared in direct conversation.\n\n"
    "STYLE:\n"
    "- Be friendly, calm and encouraging.\n"
    "- Keep replies short: usually 2–5 sentences.\n"
    "- You are not a general internet chatbot; keep focus around Dennis, Denarixx, creative/AI topics, "
    "and helpful high-level guidance.\n"
)

class ChatRequest(BaseModel):
    message: str
    detected_language: Optional[str] = None  # ignored


class ChatResponse(BaseModel):
    reply: str


def _extract_reply(data: Any) -> Optional[str]:
    """Extract assistant text from OpenAI-like or other shapes."""
    if data is None:
        return None
    if isinstance(data, str):
        return data.strip() or None
    if isinstance(data, dict):
        # OpenAI-like
        try:
            content = data["choices"][0]["message"]["content"]
            if isinstance(content, str) and content.strip():
                return content.strip()
        except Exception:
            pass

        # Fallbacks
        for k in ("reply", "response", "answer", "message", "text", "output"):
            v = data.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()

    return None


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    user_text = (payload.message or "").strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="message is required")

    api_body = {
        "model": MATRIX_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        "temperature": 0.6,
        "max_tokens": 400,
    }

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            r = await client.post(MATRIX_COMPLETIONS_URL, json=api_body)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="Error contacting AI service") from exc

    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"AI service returned status {r.status_code}")

    try:
        data = r.json()
    except ValueError:
        # Not JSON
        return ChatResponse(reply=r.text.strip() or "No reply from AI service.")

    reply = _extract_reply(data) or str(data)
    return ChatResponse(reply=reply.strip())


@app.get("/health")
def health():
    return {"ok": True, "message": "DennisChat backend is running."}