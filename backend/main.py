from __future__ import annotations

from typing import Optional, Any
import os
import json

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI(title="DennisChat Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)

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
    "- You may also answer general, light questions about AI, creativity, and careers, "
    "but keep them short and not too technical.\n\n"
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
    "- Keep focus around Dennis, Denarixx, creative/AI topics, and helpful high-level guidance.\n"
)


class ChatRequest(BaseModel):
    message: str
    detected_language: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str


def _extract_reply(data: Any) -> Optional[str]:
    if data is None:
        return None

    if isinstance(data, str):
        return data.strip() or None

    if isinstance(data, dict):
        candidates = data.get("candidates")
        if isinstance(candidates, list) and candidates:
            first = candidates[0] or {}

            content = first.get("content")
            if isinstance(content, dict):
                parts = content.get("parts")
                if isinstance(parts, list):
                    texts = []
                    for part in parts:
                        if isinstance(part, dict):
                            txt = part.get("text")
                            if isinstance(txt, str) and txt.strip():
                                texts.append(txt.strip())
                    if texts:
                        return "\n".join(texts)

            output_text = first.get("output_text")
            if isinstance(output_text, str) and output_text.strip():
                return output_text.strip()

        for key in ("reply", "response", "answer", "text", "output"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0] or {}

            message = first.get("message")
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()

                if isinstance(content, list):
                    texts = []
                    for item in content:
                        if isinstance(item, dict):
                            txt = item.get("text")
                            if isinstance(txt, str) and txt.strip():
                                texts.append(txt.strip())
                    if texts:
                        return "\n".join(texts)

            delta = first.get("delta")
            if isinstance(delta, dict):
                content = delta.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()

    return None


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    user_text = (payload.message or "").strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="message is required")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set")

    api_body = {
        "system_instruction": {
            "parts": [
                {"text": SYSTEM_PROMPT}
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": user_text}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.6,
            "maxOutputTokens": 300
        }
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                GEMINI_API_URL,
                json=api_body,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": api_key,
                },
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="Error contacting Gemini service") from exc

    raw_text = r.text

    if r.status_code != 200:
      raise HTTPException(
          status_code=502,
          detail=f"Gemini status {r.status_code}: {raw_text[:1200]}"
      )

    try:
        data = r.json()
    except ValueError:
        raise HTTPException(status_code=502, detail=f"Gemini returned non-JSON: {raw_text[:1200]}")

    reply = _extract_reply(data)
    if not reply:
        print("DEBUG GEMINI RAW RESPONSE:", json.dumps(data, ensure_ascii=False)[:4000], flush=True)
        raise HTTPException(
            status_code=502,
            detail=f"Gemini returned JSON but no extractable text: {json.dumps(data, ensure_ascii=False)[:1200]}"
        )

    return ChatResponse(reply=reply.strip())


@app.get("/health")
def health():
    return {"ok": True, "message": "DennisChat backend is running."}
