# backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx

app = FastAPI()

# --- CORS: allow your frontend to call this backend from denarixx.com + local dev ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://denarixx.com",
        "https://www.denarixx.com",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MATRIX_BASE_URL = "https://firebase-ai-models.matrixzat99.workers.dev/"
MATRIX_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "You are DennisChat, the official AI assistant on the personal website "
    "of Dennis Charles (Denarixx).\n\n"
    "LANGUAGE:\n"
    "- ALWAYS reply in the same language as the last user message.\n"
    "- If the user writes English, answer in English. If German, answer in German, etc.\n\n"
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
    "and helpful high-level guidance.\n\n"
)

class ChatRequest(BaseModel):
  message: str
  detected_language: Optional[str] = None

class ChatResponse(BaseModel):
  reply: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
  lang = payload.detected_language or "EN"

  # Build prompt for Matrix X simple `?query=` API
  prompt = (
      SYSTEM_PROMPT
      + f"User language code (hint): {lang}\n"
      + f"User: {payload.message}\n"
      + "Assistant:"
  )

  params = {
      "query": prompt,
      "model": MATRIX_MODEL,
  }

  try:
      async with httpx.AsyncClient(timeout=20.0) as client:
          r = await client.get(MATRIX_BASE_URL, params=params)
  except httpx.RequestError as exc:
      raise HTTPException(
          status_code=502,
          detail="Error contacting AI service",
      ) from exc

  if r.status_code != 200:
      raise HTTPException(
          status_code=502,
          detail=f"AI service returned status {r.status_code}",
      )

  # Try to parse JSON, fall back to text
  try:
      data = r.json()
  except ValueError:
      # Not JSON
      return ChatResponse(reply=r.text)

  # Matrix X typical shape:
  # {
  #   "success": true,
  #   "message": { "role": "assistant", "content": "..." },
  #   "model_used": "gpt-4o-mini"
  # }
  if isinstance(data, str):
      reply = data
  else:
      msg = data.get("message")

      if isinstance(msg, dict):
          # Prefer the assistant content
          reply = msg.get("content") or msg.get("text") or str(msg)
      elif isinstance(msg, str):
          reply = msg
      else:
          # Fallbacks for other possible shapes
          reply = (
                  data.get("reply")
                  or data.get("response")
                  or data.get("answer")
                  or str(data)
          )

  return ChatResponse(reply=reply)

# Optional: avoid 404 on "/" (purely cosmetic)
@app.get("/")
def root():
  return {"status": "ok", "message": "DennisChat backend is running."}
