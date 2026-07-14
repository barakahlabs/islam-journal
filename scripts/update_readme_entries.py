#!/usr/bin/env python3
"""Regenerate the Entries list in README.md from published posts.

Run after adding or editing entries under content/posts/, before committing:

    python3 scripts/update_readme_entries.py
"""
import csv
import io
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
START = "<!-- ENTRIES:START -->"
END = "<!-- ENTRIES:END -->"


def published_posts():
    result = subprocess.run(
        ["hugo", "list", "all"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    rows = csv.DictReader(io.StringIO(result.stdout))
    posts = [
        row
        for row in rows
        if row["section"] == "posts" and row["draft"] == "false"
    ]
    posts.sort(key=lambda row: row["date"], reverse=True)
    return posts


def render(posts):
    lines = [f"- [{row['title']}]({row['permalink']})" for row in posts]
    return "\n".join(lines)


def main():
    posts = published_posts()
    entries_md = render(posts)

    text = README.read_text()
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    if not pattern.search(text):
        print(f"Could not find {START} / {END} markers in README.md", file=sys.stderr)
        sys.exit(1)

    replacement = f"{START}\n{entries_md}\n{END}"
    README.write_text(pattern.sub(replacement, text))
    print(f"Updated README.md with {len(posts)} entr{'y' if len(posts) == 1 else 'ies'}.")


if __name__ == "__main__":
    main()
