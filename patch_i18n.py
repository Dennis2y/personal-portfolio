import re
from pathlib import Path

path = Path("index.html")
s = path.read_text(encoding="utf-8")

new_func = r'''
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
'''

# Replace the existing loadLanguage function only
pattern = r'async function loadLanguage\(lang\)\s*{.*?}\s*'
m = re.search(pattern, s, flags=re.DOTALL)
if not m:
    raise SystemExit("❌ Could not find: async function loadLanguage(lang) { ... } in index.html")

s2 = re.sub(pattern, new_func.strip()+"\n", s, count=1, flags=re.DOTALL)

path.write_text(s2, encoding="utf-8")
print("✅ Patched index.html: loadLanguage() now uses URL-based paths + logging.")
