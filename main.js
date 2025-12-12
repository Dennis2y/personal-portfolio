// --- DennisChat keyword-based brain ---
// =======================
// i18n (Languages) - Robust loader
// =======================

const SUPPORTED_LANGS = ["en","de","fr","es","it","pt","ar","ru","zh"];
const DEFAULT_LANG = "en";

let I18N_EN = null;     // flattened English dict
let I18N_DICT = null;   // flattened current dict

function flatten(obj, prefix = "", out = {}) {
  for (const [k, v] of Object.entries(obj || {})) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === "object" && !Array.isArray(v)) flatten(v, key, out);
    else out[key] = String(v);
  }
  return out;
}

function getLangUrl(lang) {
  // ✅ works in subfolders + github pages + local files
  const base = new URL(".", window.location.href);
  const url = new URL(`lang/${lang}.json`, base);
  // Avoid caching while debugging
  url.searchParams.set("v", String(Date.now()));
  return url.toString();
}

async function fetchLangJson(lang) {
  const url = getLangUrl(lang);
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to load ${lang}.json (${res.status}) at ${url}`);
  const raw = await res.json(); // will throw if JSON invalid
  return flatten(raw);
}

function t(key) {
  return (I18N_DICT && I18N_DICT[key]) || (I18N_EN && I18N_EN[key]) || key;
}

function applyTranslations() {
  // Text / HTML
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.getAttribute("data-i18n"));
  });
  document.querySelectorAll("[data-i18n-html]").forEach((el) => {
    el.innerHTML = t(el.getAttribute("data-i18n-html"));
  });

  // Placeholders
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.setAttribute("placeholder", t(el.getAttribute("data-i18n-placeholder")));
  });

  // Optional: any attribute like title/aria-label
  document.querySelectorAll("[data-i18n-attr]").forEach((el) => {
    // format: data-i18n-attr="title:chat.subtitle,aria-label:nav.contact"
    const spec = el.getAttribute("data-i18n-attr") || "";
    spec.split(",").map(s => s.trim()).filter(Boolean).forEach(pair => {
      const [attr, key] = pair.split(":").map(x => x.trim());
      if (attr && key) el.setAttribute(attr, t(key));
    });
  });
}

function setDirAndLang(lang) {
  document.documentElement.setAttribute("lang", lang);
  document.documentElement.setAttribute("dir", lang === "ar" ? "rtl" : "ltr");
}

function setLangLabel(lang) {
  const label = document.getElementById("lang-current-label");
  if (label) label.textContent = lang.toUpperCase();
}

async function setLanguage(lang) {
  const safe = SUPPORTED_LANGS.includes(lang) ? lang : DEFAULT_LANG;

  try {
    if (!I18N_EN) I18N_EN = await fetchLangJson("en");
    I18N_DICT = safe === "en" ? I18N_EN : await fetchLangJson(safe);

    localStorage.setItem("lang", safe);
    setDirAndLang(safe);
    setLangLabel(safe);
    applyTranslations();
    // console.log("✅ Language loaded:", safe);
  } catch (err) {
    console.error("❌ i18n failed:", err);
    // fallback
    if (!I18N_EN) {
      // last resort: no translations at all
      return;
    }
    I18N_DICT = I18N_EN;
    localStorage.setItem("lang", "en");
    setDirAndLang("en");
    setLangLabel("en");
    applyTranslations();
  }
}

function initLangMenu() {
  const trigger = document.getElementById("lang-trigger");
  const menu = document.getElementById("lang-menu");
  if (!trigger || !menu) return;

  // Toggle menu
  trigger.addEventListener("click", () => {
    const open = trigger.getAttribute("aria-expanded") === "true";
    trigger.setAttribute("aria-expanded", String(!open));
    menu.classList.toggle("open", !open);
  });

  // Close on outside click
  document.addEventListener("click", (e) => {
    if (!menu.contains(e.target) && !trigger.contains(e.target)) {
      trigger.setAttribute("aria-expanded", "false");
      menu.classList.remove("open");
    }
  });

  // Select language
  menu.querySelectorAll(".lang-option").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const lang = btn.getAttribute("data-lang");
      trigger.setAttribute("aria-expanded", "false");
      menu.classList.remove("open");
      await setLanguage(lang);
    });
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  initLangMenu();
  const saved = (localStorage.getItem("lang") || DEFAULT_LANG).toLowerCase();
  await setLanguage(saved);
});