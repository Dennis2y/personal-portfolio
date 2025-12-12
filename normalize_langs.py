import json, re, shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(".")
LANG_DIR = ROOT / "lang"
INDEX = ROOT / "index.html"

def extract_keys_from_index(html: str):
    keys = re.findall(r'data-i18n="([^"]+)"', html)
    # remove duplicates, preserve order
    seen = set()
    out = []
    for k in keys:
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out

def flatten_any(obj, prefix=""):
    """
    Flattens dicts into {"a.b.c": value}.
    If keys already contain dots (e.g. "ai.desc"), we keep them as dotted paths.
    """
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            k = str(k)
            new_prefix = f"{prefix}.{k}" if prefix else k
            out.update(flatten_any(v, new_prefix))
    else:
        # leaf: string/number/bool/null/list -> keep as-is (your files are mostly strings)
        out[prefix] = obj
    return out

def set_nested(d, path, value):
    parts = path.split(".")
    cur = d
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value

def nested_from_flat(flat_map):
    d = {}
    for k, v in flat_map.items():
        if not k:
            continue
        set_nested(d, k, v)
    return d

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def main():
    if not LANG_DIR.exists():
        raise SystemExit("❌ lang/ folder not found.")

    # Keys used by the site (from index.html)
    html = INDEX.read_text(encoding="utf-8")
    required_keys = extract_keys_from_index(html)

    # Use en.json as fallback values (for missing keys)
    en_path = LANG_DIR / "en.json"
    if not en_path.exists():
        raise SystemExit("❌ lang/en.json not found (needed as fallback).")

    en_raw = load_json(en_path)
    en_flat = flatten_any(en_raw)

    # Backup folder
    backup_dir = LANG_DIR / ("_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    backup_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(LANG_DIR.glob("*.json"))
    if not files:
        raise SystemExit("❌ No json files found in lang/")

    print("✅ Found", len(files), "language files.")
    print("✅ Found", len(required_keys), "data-i18n keys in index.html.")

    for f in files:
        raw = load_json(f)
        flat = flatten_any(raw)

        # Build final flat mapping with required keys only
        final_flat = {}
        missing = []
        for k in required_keys:
            if k in flat:
                final_flat[k] = flat[k]
            elif k in en_flat:
                # Fill missing with EN so UI is never blank
                final_flat[k] = en_flat[k]
                missing.append(k)
            else:
                # If key not even in EN fallback, skip
                pass

        final_nested = nested_from_flat(final_flat)

        # Backup then overwrite normalized file
        shutil.copy2(f, backup_dir / f.name)
        save_json(f, final_nested)

        if missing:
            print(f"🟡 {f.name}: normalized (filled {len(missing)} missing keys from EN)")
        else:
            print(f"🟢 {f.name}: normalized (no missing keys)")

    print("\n✅ Done. Backups saved in:", backup_dir)

if __name__ == "__main__":
    main()
