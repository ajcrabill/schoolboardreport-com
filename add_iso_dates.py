#!/usr/bin/env python3
"""Add ISO date: field to analysis HTML front matter based on date_display."""
import os
import re
from datetime import datetime

ANALYSIS_DIR = os.path.join(os.path.dirname(__file__), "analysis")

MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12,
}

def parse_date_display(s):
    """Parse 'June 16, 2026' or 'June 2026' into ISO string."""
    s = s.strip().strip('"').strip("'")
    # Try "Month Day, Year"
    m = re.match(r'^(\w+)\s+(\d+),\s+(\d{4})$', s)
    if m:
        month_name, day, year = m.group(1), int(m.group(2)), int(m.group(3))
        month = MONTH_MAP.get(month_name)
        if month:
            return f"{year:04d}-{month:02d}-{day:02d}"
    # Try "Month Year"
    m = re.match(r'^(\w+)\s+(\d{4})$', s)
    if m:
        month_name, year = m.group(1), int(m.group(2))
        month = MONTH_MAP.get(month_name)
        if month:
            return f"{year:04d}-{month:02d}-01"
    return None

def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Must start with front matter
    if not content.startswith("---"):
        print(f"  SKIP (no front matter): {os.path.basename(path)}")
        return

    # Find end of front matter
    end = content.index("---", 3)
    front = content[3:end]
    rest = content[end:]  # includes closing ---

    # Already has date:?
    if re.search(r'^date:', front, re.MULTILINE):
        print(f"  SKIP (already has date:): {os.path.basename(path)}")
        return

    # Find date_display
    m = re.search(r'^date_display:\s*(.+)$', front, re.MULTILINE)
    if not m:
        print(f"  SKIP (no date_display): {os.path.basename(path)}")
        return

    iso = parse_date_display(m.group(1))
    if not iso:
        print(f"  ERROR parsing date_display '{m.group(1)}': {os.path.basename(path)}")
        return

    # Insert date: after date_display line
    new_front = re.sub(
        r'(^date_display:\s*.+$)',
        r'\1\ndate: "' + iso + '"',
        front,
        flags=re.MULTILINE
    )

    new_content = "---" + new_front + rest
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  ADDED date: {iso}  ({os.path.basename(path)})")

if __name__ == "__main__":
    files = sorted(f for f in os.listdir(ANALYSIS_DIR) if f.endswith(".html"))
    print(f"Processing {len(files)} files in {ANALYSIS_DIR}...")
    for fname in files:
        process_file(os.path.join(ANALYSIS_DIR, fname))
    print("Done.")
