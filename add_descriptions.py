#!/usr/bin/env python3
"""Add description: field to analysis HTML front matter from lede paragraph."""
import os
import re

ANALYSIS_DIR = os.path.join(os.path.dirname(__file__), "analysis")

def extract_lede(content):
    m = re.search(r'<p class="lede">([^<]+)', content)
    if m:
        text = m.group(1).strip()
        # Truncate to ~200 chars at word boundary
        if len(text) > 220:
            text = text[:220].rsplit(' ', 1)[0] + '…'
        return text
    return None

def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        print(f"  SKIP (no front matter): {os.path.basename(path)}")
        return

    end = content.index("---", 3)
    front = content[3:end]
    rest = content[end:]

    # Already has description:?
    if re.search(r'^description:', front, re.MULTILINE):
        print(f"  SKIP (already has description:): {os.path.basename(path)}")
        return

    lede = extract_lede(content)
    if not lede:
        print(f"  SKIP (no lede): {os.path.basename(path)}")
        return

    # Escape any double quotes in lede
    lede_escaped = lede.replace('"', '\\"')

    # Insert description: after title line
    new_front = re.sub(
        r'(^title:\s*.+$)',
        r'\1\ndescription: "' + lede_escaped + '"',
        front,
        count=1,
        flags=re.MULTILINE
    )

    new_content = "---" + new_front + rest
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  ADDED description ({len(lede)} chars): {os.path.basename(path)}")

if __name__ == "__main__":
    files = sorted(f for f in os.listdir(ANALYSIS_DIR) if f.endswith(".html"))
    print(f"Processing {len(files)} files...")
    for fname in files:
        process_file(os.path.join(ANALYSIS_DIR, fname))
    print("Done.")
