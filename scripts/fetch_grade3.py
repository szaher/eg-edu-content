#!/usr/bin/env python3
"""Fetch Egyptian Grade 3 curriculum PDFs for local processing.

The Ministry Grade 3 catalog is currently unreliable for direct access
(blank/403 for some clients). This script therefore uses a verified independent
mirror index to discover Ministry-issued 2026/2027 Grade 3 files.

The files are stored under downloads/ and are intentionally excluded from Git.
Do not republish them unless you have confirmed redistribution rights.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

INDEX = (
    "https://natega24.com/moe/"
    "moe-%D8%A7%D9%84%D8%B5%D9%81-%D8%A7%D9%84%D8%AB%D8%A7%D9%84%D8%AB-"
    "%D8%A7%D9%84%D8%A7%D8%A8%D8%AA%D8%AF%D8%A7%D8%A6%D9%8A.html"
)
OUT = Path("downloads/grade-3")
HREF_RE = re.compile(r'''href=["']([^"']+)["']''', re.I)


def fetch(url: str) -> bytes:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html,application/pdf,*/*",
        },
    )
    with urlopen(req, timeout=60) as resp:
        return resp.read()


def hrefs(page_url: str, body: bytes) -> list[str]:
    text = body.decode("utf-8", errors="ignore")
    return [
        urljoin(page_url, html.unescape(href))
        for href in HREF_RE.findall(text)
    ]


def is_subject_page(url: str) -> bool:
    parsed = urlparse(url)
    return (
        parsed.hostname == "natega24.com"
        and parsed.path.startswith("/moe/moe-")
        and "html" in parsed.path
    )


def is_pdf(url: str) -> bool:
    parsed = urlparse(url)
    return (
        parsed.hostname == "natega24.com"
        and parsed.path.startswith("/assets/moe/books/")
        and parsed.path.lower().endswith(".pdf")
    )


def safe_name(url: str, number: int) -> str:
    name = unquote(Path(urlparse(url).path).name)
    name = re.sub(r"[^\w.\-()\[\] \u0600-\u06ff]+", "_", name, flags=re.UNICODE)
    return name or f"grade3-{number}.pdf"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    try:
        index_body = fetch(INDEX)
    except Exception as exc:
        print(f"Could not read Grade 3 index: {exc}", file=sys.stderr)
        print(f"Open manually: {INDEX}")
        return 1

    subject_pages = sorted({u for u in hrefs(INDEX, index_body) if is_subject_page(u)})
    if not subject_pages:
        print("No Grade 3 subject pages were discovered.", file=sys.stderr)
        return 2

    print(f"Found {len(subject_pages)} subject page(s).")
    pdfs: set[str] = set()

    for page in subject_pages:
        try:
            body = fetch(page)
        except Exception as exc:
            print(f"SKIP {page}: {exc}", file=sys.stderr)
            continue
        pdfs.update(u for u in hrefs(page, body) if is_pdf(u))

    links = sorted(pdfs)
    if not links:
        print("No PDF links were discovered.", file=sys.stderr)
        return 3

    print(f"Found {len(links)} PDF(s).")
    for i, url in enumerate(links, start=1):
        dest = OUT / safe_name(url, i)
        try:
            data = fetch(url)
            if not data.startswith(b"%PDF"):
                raise ValueError("response is not a PDF")
            dest.write_bytes(data)
            print(f"[{i}/{len(links)}] {dest}")
        except Exception as exc:
            print(f"[{i}/{len(links)}] FAILED {url}: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
