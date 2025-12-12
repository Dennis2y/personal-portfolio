from pathlib import Path
import re

p = Path("backend/main.py")
s = p.read_text(encoding="utf-8")

# 1) Ensure imports exist
need_staticfiles = "from fastapi.staticfiles import StaticFiles" not in s
need_pathlib = "from pathlib import Path" not in s

if need_staticfiles or need_pathlib:
    # Insert imports after the first fastapi import block
    lines = s.splitlines(True)
    insert_at = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("from fastapi") or line.strip().startswith("import"):
            insert_at = i + 1
    extra = ""
    if need_pathlib:
        extra += "from pathlib import Path\n"
    if need_staticfiles:
        extra += "from fastapi.staticfiles import StaticFiles\n"
    lines.insert(insert_at, extra)
    s = "".join(lines)

# 2) Add static mount at the END (so /api routes keep working)
mount_snippet = r'''
# --- Serve frontend (static) ---
BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/", StaticFiles(directory=str(BASE_DIR), html=True), name="site")
'''

if "app.mount(\"/\", StaticFiles" not in s:
    s = s.rstrip() + "\n\n" + mount_snippet.strip() + "\n"
    p.write_text(s, encoding="utf-8")
    print("✅ Patched backend/main.py: added static frontend mount at '/'.")
else:
    print("ℹ️ backend/main.py already has a StaticFiles mount. No changes made.")
