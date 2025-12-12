// scripts/chatbot.js – DennisChat → FastAPI backend on Render (multilingual + live typing)

(function () {
  const API_URL = "https://dennischat-backend.onrender.com/chat";
  console.log("🔥 DennisChat JS loaded – API_URL =", API_URL);

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

  // Keep a reference so we can update the welcome message if language changes
  let welcomeBubbleEl = null;
  let currentLang = "en";
  let strings = {
    welcome: "Hi, I’m DennisChat 🤖 I can answer questions about Dennis, Denarixx, this site, and some high-level AI/creative topics. Ask me anything.",
    thinking: "Thinking…",
    error: "⚠️ I couldn’t reach the AI service right now. Please try again in a moment."
  };

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

  function setSendingState(value) {
    isSending = value;
    input.disabled = value;
    const submitBtn = form.querySelector("button[type='submit']");
    if (submitBtn) submitBtn.disabled = value;
  }

  // 🟣 Fast typewriter effect
  async function typeText(bubble, text, speed = 14) {
    if (!text || text.length > 1200) {
      bubble.textContent = text || "";
      scrollToBottom();
      return;
    }

    bubble.textContent = "";
    for (let i = 0; i < text.length; i++) {
      bubble.textContent += text[i];
      scrollToBottom();
      // eslint-disable-next-line no-await-in-loop
      await new Promise((res) => setTimeout(res, speed));
    }
  }

  // ---------- I18N HELPERS ----------
  function baseLang(code) {
    return String(code || "").toLowerCase().split("-")[0];
  }

  function getCurrentLang() {
    // priority: window global set by index i18n → localStorage.lang → <html lang>
    const fromGlobal = baseLang(window.__DENNIS_LANG__);
    if (fromGlobal) return fromGlobal;

    let stored = "";
    try { stored = localStorage.getItem("lang") || ""; } catch (_) {}
    stored = baseLang(stored);
    if (stored) return stored;

    return baseLang(document.documentElement.lang) || "en";
  }

  async function fetchJson(url) {
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) throw new Error("HTTP " + res.status);
    return await res.json();
  }

  async function loadLangDict(lang) {
    const safe = baseLang(lang) || "en";
    const urls = [
      `lang/${safe}.json`,
      `/lang/${safe}.json`,
      new URL(`lang/${safe}.json`, window.location.href).toString()
    ];

    for (const u of urls) {
      try {
        return await fetchJson(u);
      } catch (_) {}
    }
    return null;
  }

  function t(dict, key, fallback = null) {
    if (!dict || typeof dict !== "object") return fallback;
    const parts = key.split(".");
    let v = dict;
    for (const p of parts) {
      if (v && typeof v === "object" && p in v) v = v[p];
      else return fallback;
    }
    return typeof v === "string" ? v : fallback;
  }

  async function refreshChatLanguage() {
    const lang = getCurrentLang();
    currentLang = lang;

    // (Optional) RTL support for Arabic
    if (lang === "ar") document.documentElement.setAttribute("dir", "rtl");
    else document.documentElement.removeAttribute("dir");

    const dict = (await loadLangDict(lang)) || (await loadLangDict("en"));

    // Prefer chat.welcome, fallback to chat.greeting (your older key), then English default
    strings.welcome =
      t(dict, "chat.welcome", null) ||
      t(dict, "chat.greeting", null) ||
      strings.welcome;

    // Optional keys (if you add them later)
    strings.thinking = t(dict, "chat.thinking", strings.thinking);
    strings.error    = t(dict, "chat.error", strings.error);

    // If the welcome bubble exists, update it immediately when language changes
    if (welcomeBubbleEl) {
      welcomeBubbleEl.textContent = strings.welcome;
      scrollToBottom();
    }
  }

  // Listen to your index.html event (we dispatch it there)
  window.addEventListener("dennis:langChanged", () => {
    refreshChatLanguage();
  });

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

  // ---------- INITIAL WELCOME MESSAGE (translated) ----------
  (async function initialWelcome() {
    await refreshChatLanguage();
    welcomeBubbleEl = createMsgBubble("bot");
    welcomeBubbleEl.textContent = strings.welcome;
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
    botBubble.textContent = strings.thinking;

    setSendingState(true);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: rawText })
      });

      if (!res.ok) {
        let detail = `Error ${res.status}`;
        try {
          const data = await res.json();
          if (data && (data.detail || data.error)) detail = data.detail || data.error;
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

      await typeText(botBubble, reply, 14);
    } catch (err) {
      console.error("DennisChat backend error:", err);
      botBubble.textContent = strings.error;
    } finally {
      setSendingState(false);
      scrollToBottom();
    }
  });
})();