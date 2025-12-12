import re
from pathlib import Path

p = Path("index.html")
s = p.read_text(encoding="utf-8")

# 1) Replace loadLanguage(lang) with URL-based fetch (works in subfolders + better logging)
new_load = r'''
    async function loadLanguage(lang) {
      const primaryUrl  = new URL(`lang/${lang}.json`, window.location.href);
      const fallbackUrl = new URL(`lang/en.json`, window.location.href);

      try {
        const res = await fetch(primaryUrl, { cache: "no-store" });
        if (!res.ok) throw new Error(`HTTP ${res.status} for ${primaryUrl}`);
        return await res.json();
      } catch (e) {
        console.warn("[i18n] Failed loading", lang, "→", e);

        try {
          const fallback = await fetch(fallbackUrl, { cache: "no-store" });
          if (!fallback.ok) throw new Error(`HTTP ${fallback.status} for ${fallbackUrl}`);
          return await fallback.json();
        } catch (e2) {
          console.error("[i18n] Failed loading fallback EN:", e2);
          return null;
        }
      }
    }
'''.strip() + "\n"

load_pat = r'async function loadLanguage\(lang\)\s*{.*?}\s*'
if re.search(load_pat, s, flags=re.DOTALL):
    s = re.sub(load_pat, new_load, s, count=1, flags=re.DOTALL)
else:
    raise SystemExit("❌ Could not find loadLanguage(lang) function in index.html")

# 2) Replace the translation apply block to support BOTH nested and dotted keys
new_apply = r'''
      function i18nGet(dict, key) {
        if (!dict || !key) return undefined;
        const parts = String(key).split(".");
        let cur = dict;

        for (let i = 0; i < parts.length; i++) {
          const k = parts[i];

          if (cur && Object.prototype.hasOwnProperty.call(cur, k)) {
            cur = cur[k];
            continue;
          }

          // Fallback: try remaining path as a single dotted key, e.g. "ai.desc"
          const remaining = parts.slice(i).join(".");
          if (cur && Object.prototype.hasOwnProperty.call(cur, remaining)) {
            return cur[remaining];
          }

          return undefined;
        }
        return cur;
      }

      document.querySelectorAll("[data-i18n]").forEach((el) => {
        const key = el.getAttribute("data-i18n");
        const txt = i18nGet(dict, key);

        if (txt !== undefined && txt !== null) {
          el.innerHTML = txt;
        }
      });
'''.strip() + "\n"

apply_pat = r'document\.querySelectorAll\("\[data-i18n\]"\)\.forEach\(\(el\)\s*=>\s*{.*?}\);\s*'
if re.search(apply_pat, s, flags=re.DOTALL):
    s = re.sub(apply_pat, new_apply, s, count=1, flags=re.DOTALL)
else:
    raise SystemExit('❌ Could not find the data-i18n apply loop in index.html')

p.write_text(s, encoding="utf-8")
print("✅ Patched index.html: i18n fetch fixed + dotted keys supported.")
