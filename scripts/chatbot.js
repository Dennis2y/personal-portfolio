/* =======================
   CHATBOT FRONTEND LOGIC
========================== */

const CHAT_API_URL = "http://127.0.0.1:8001/api/chat";  // 🔥 your backend
let chatWindow = null;

document.addEventListener("DOMContentLoaded", () => {
    const launcher = document.querySelector(".chat-launcher");
    chatWindow = document.querySelector(".chat-window");
    const closeBtn = document.querySelector(".chat-close");
    const sendBtn = document.querySelector(".chat-send-btn");
    const input = document.querySelector(".chat-input");
    const messages = document.querySelector(".chat-messages");

    launcher.addEventListener("click", () => {
        chatWindow.classList.toggle("open");
    });

    closeBtn.addEventListener("click", () => {
        chatWindow.classList.remove("open");
    });

    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    function addMessage(text, sender = "bot") {
        const div = document.createElement("div");
        div.className = `msg msg-${sender}`;
        div.innerHTML = `<div class="msg-bubble">${text}</div>`;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }

    async function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        addMessage(text, "user");
        input.value = "";

        // Bot typing indicator
        const typing = document.createElement("div");
        typing.className = "msg msg-bot";
        typing.innerHTML = `<div class="msg-bubble">Typing...</div>`;
        messages.appendChild(typing);
        messages.scrollTop = messages.scrollHeight;

        try {
            const res = await fetch(CHAT_API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: text,
                    // The backend will autodetect languages
                    input_lang: null,
                    ui_lang: document.documentElement.lang || "en"
                })
            });

            const data = await res.json();
            typing.remove();
            addMessage(data.reply, "bot");
        } catch (err) {
            typing.remove();
            addMessage("⚠️ Error connecting to chatbot.", "bot");
        }
    }
});