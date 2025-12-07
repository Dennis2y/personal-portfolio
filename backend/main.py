# backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx
import re

app = FastAPI()

# --- CORS: allow ANY origin (localhost + denarixx.com etc.) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # allow all origins (you can restrict later)
    allow_credentials=False,      # no cookies/sessions needed
    allow_methods=["*"],
    allow_headers=["*"],
)

MATRIX_BASE_URL = "https://firebase-ai-models.matrixzat99.workers.dev/"
MATRIX_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "You are DennisChat, the official AI assistant on the personal website "
    "of Dennis Charles (Denarixx).\n\n"
    "LANGUAGE RULES:\n"
    "- You will receive a language code like EN, DE, ES, AR, etc.\n"
    "- ALWAYS reply ONLY in that language code, even if the user mixes other languages.\n"
    "- Do NOT switch languages by yourself.\n\n"
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


# ---------- SIMPLE GREETING DETECTION ----------

def is_simple_greeting(text: str) -> bool:
    """
    Return True if the user message is basically just a greeting
    (like 'hi', 'hello', 'good morning', 'hola', 'صباح الخير', etc.)
    so we can safely reply with a fixed greeting without calling the AI.
    """
    t = text.strip().lower()

    # If it's long, it's probably not just a greeting
    if len(t.split()) > 5:
        return False

    patterns = [
        r"^hi\b",
        r"^hello\b",
        r"^hey\b",
        r"good\s+morning",
        r"good\s+evening",
        r"good\s+afternoon",
        r"\bhola\b",
        r"\bhallo\b",
        r"\bbonjour\b",
        r"\bciao\b",
        r"\bolá\b|\bola\b",
        r"صباح الخير",
    ]

    return any(re.search(p, t) for p in patterns)


def greeting_for_lang(lang: str) -> str:
    """
    Return a friendly greeting in the target language.
    Used only when the message is a simple greeting.
    """
    lang = lang.upper()

    if lang == "DE":
        return (
            "Guten Morgen! Wie kann ich Ihnen heute helfen? "
            "Wenn Sie Fragen zu Dennis, Denarixx oder kreativen Themen haben, stehe ich Ihnen gerne zur Verfügung."
        )
    if lang == "ES":
        return (
            "¡Hola! ¿En qué puedo ayudarte hoy? Si tienes preguntas sobre Dennis Charles, sus proyectos Denarixx "
            "o temas creativos/IA, estaré encantado de responder."
        )
    if lang == "AR":
        return (
            "صباح النور! كيف يمكنني مساعدتك اليوم؟ إذا كان لديك أي أسئلة حول دينيس أو مشاريع Denarixx "
            "أو مواضيع عن الإبداع والذكاء الاصطناعي، فلا تتردد في طرحها."
        )
    if lang == "FR":
        return (
            "Bonjour ! Comment puis-je t’aider aujourd’hui ? "
            "Je peux répondre à tes questions sur Dennis, Denarixx ou des sujets créatifs/IA."
        )
    if lang == "IT":
        return (
            "Ciao! Come posso aiutarti oggi? Posso rispondere a domande su Dennis, Denarixx "
            "e argomenti creativi o legati all’IA."
        )
    if lang == "PT":
        return (
            "Olá! Como posso te ajudar hoje? Posso responder perguntas sobre Dennis, os projetos Denarixx "
            "e temas de criatividade e IA."
        )
    if lang == "RU":
        return (
            "Привет! Чем я могу помочь сегодня? Я могу рассказать о Деннисе, его проектах Denarixx "
            "и ответить на общие вопросы об ИИ и творчестве."
        )
    if lang == "ZH":
        return (
            "你好！今天我可以帮你什么？我可以回答关于 Dennis、Denarixx 项目，以及一些关于 AI 和创意的问题。"
        )
    if lang == "HI":
        return (
            "नमस्ते! मैं आज आपकी कैसे मदद कर सकता हूँ? मैं Dennis, Denarixx प्रोजेक्ट्स और AI/क्रिएटिव से जुड़े "
            "सवालों का जवाब दे सकता हूँ।"
        )

    # Default: English
    return (
        "Good morning! How can I help you today? I can answer questions about Dennis, Denarixx, "
        "this site, and some high-level AI/creative topics."
    )


# ---------- MAIN CHAT ENDPOINT ----------

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    # Normalize language code (e.g. "en" -> "EN")
    lang = (payload.detected_language or "EN").upper()
    user_text = payload.message or ""

    # 1) If it's a simple greeting, answer directly (no AI call)
    if is_simple_greeting(user_text):
        return ChatResponse(reply=greeting_for_lang(lang))

    # 2) Otherwise, call the Matrix X model
    prompt = (
        SYSTEM_PROMPT
        + f"User language code: {lang}\n"
        + "IMPORTANT:\n"
        + f"- You MUST reply ONLY in the language matching this code: {lang}.\n"
        + "- Do NOT switch languages, even if the user mixes words.\n\n"
        + f"User ({lang}): {user_text}\n"
        + f"Assistant ({lang}):"
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