// scripts/chatbot.js – DennisChat via FastAPI backend (no direct Matrix call in browser)

(function () {
  const API_URL = "https://personal-portfolio.onrender.com/chat";

  const launcher   = document.getElementById("chat-launcher");
  const chatWindow = document.getElementById("chat-window");
  const closeBtn   = document.getElementById("chat-close");
  const form       = document.getElementById("chat-form");
  const input      = document.getElementById("chat-input");
  const messagesEl = document.getElementById("chat-messages");

  if (!launcher || !chatWindow || !closeBtn || !form || !input || !messagesEl) {
    console.warn("DennisChat: widget elements not found in DOM.");
    return;
  }

  let isSending = false;

    // ---------- LANGUAGE DETECTOR (hint only) ----------
  function detectLanguage(text) {
    const t = text.toLowerCase();

    // Strong signals by alphabet
    if (/[ء-ي]/.test(text)) return "AR"; // Arabic
    if (/[а-яё]/i.test(text)) return "RU"; // Cyrillic
    if (/[\u4e00-\u9fff]/.test(text)) return "ZH"; // Chinese
    if (/[अ-ह]/.test(text)) return "HI"; // Devanagari

    // Explicit language keywords
    if (/hallo|tschüss|danke|ß|ä|ö|ü/.test(t)) return "DE";
    if (/bonjour|merci|fran\u00e7ais|ç|é|è|à/.test(t)) return "FR";
    if (/hola|gracias|espa\u00f1ol|¿|¡|ñ/.test(t)) return "ES";
    if (/ciao|grazie|italiano/.test(t)) return "IT";
    if (/olá|obrigado|português/.test(t)) return "PT";

    // Common English greetings / phrases
    if (/hello|^hi\b|hey\b|good morning|good afternoon|good evening/.test(t)) {
      return "EN";
    }

    // DEFAULT: if nothing else matched, assume English
    return "EN";
  }


  // ---------- UI HELPERS ----------
  function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function createMsgBubble(role) {
    const wrapper = document.createElement("div");
    wrapper.className = "msg " + (role === "user" ? "msg-user" : "msg-bot");

    const bubble = document.createElement("div");
    bubble.className = "msg-bubble";

    wrapper.appendChild(bubble);
    messagesEl.appendChild(wrapper);
    scrollToBottom();

    return bubble;
  }

  async function typeText(bubble, text, speed = 14) {
    bubble.textContent = "";
    for (let i = 0; i < text.length; i++) {
      bubble.textContent += text[i];
      scrollToBottom();
      await new Promise((res) => setTimeout(res, speed));
    }
  }

  function setSendingState(value) {
    isSending = value;
    input.disabled = value;
    const submitBtn = form.querySelector("button[type='submit']");
    if (submitBtn) submitBtn.disabled = value;
  }

  // ---------- OPEN / CLOSE WINDOW ----------
  launcher.addEventListener("click", () => {
    chatWindow.classList.add("open");
    launcher.classList.add("hidden");
    scrollToBottom();
    input.focus();
  });

  closeBtn.addEventListener("click", () => {
    chatWindow.classList.remove("open");
    setTimeout(() => launcher.classList.remove("hidden"), 220);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      chatWindow.classList.remove("open");
      setTimeout(() => launcher.classList.remove("hidden"), 220);
    }
  });

  // ---------- INITIAL WELCOME MESSAGE ----------
  (function initialWelcome() {
    const bubble = createMsgBubble("bot");
    bubble.textContent =
      "Hi, I’m DennisChat 🤖 I can answer questions about Dennis, Denarixx, this site, and some high-level AI/creative topics. Ask me anything.";
  })();

  // ---------- MAIN MESSAGE HANDLER ----------
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (isSending) return;

    const rawText = input.value.trim();
    if (!rawText) return;
    input.value = "";

    const userBubble = createMsgBubble("user");
    userBubble.textContent = rawText;

    const botBubble = createMsgBubble("bot");
    botBubble.textContent = "Thinking…";

    const langCode = detectLanguage(rawText);

    setSendingState(true);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: rawText,
          detected_language: langCode
        })
      });

      if (!res.ok) {
        let detail = `Error ${res.status}`;
        try {
          const data = await res.json();
          if (data && (data.detail || data.error)) {
            detail = data.detail || data.error;
          }
        } catch (_) {}
        throw new Error(detail);
      }

      const data = await res.json();

      const reply =
        (typeof data === "string" && data) ||
        data.reply ||
        data.message ||
        data.response ||
        "[No reply from backend]";

      await typeText(botBubble, reply, 15);
    } catch (err) {
      console.error("DennisChat backend error:", err);
      botBubble.textContent =
        "⚠️ I couldn’t reach the AI service right now. Please try again in a moment.";
    } finally {
      setSendingState(false);
      scrollToBottom();
    }
  });
})();