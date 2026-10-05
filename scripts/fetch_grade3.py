#!/usr/bin/env python3
"""Fetch Ministry-hosted Grade 3 PDFs for local use only.

The script discovers PDF links from the official Egyptian Ministry of Education
Grade 3 portal and downloads only links hosted on moe.gov.eg.

Downloaded files are intentionally excluded from Git by .gitignore.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

PORTAL = (
    "https://moe.gov.eg/ar/elearningenterypage/e-learning/"
    "?pageIndex=-4&schoolStageId=1582&schoolYearId=1933"
)
OUT = Path("downloads/grade-3")
PDF_RE = re.compile(r'''href=["']([^"']+\.pdf(?:\?[^"']*)?)["']''', re.I)


def fetch(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30) as resp:
        return resp.read()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    try:
        html = fetch(PORTAL).decode("utf-8", errors="ignore")
    except Exception as exc:
        print(f"Could not read Ministry portal: {exc}", file=sys.stderr)
        print("Open the official portal in a browser and download files manually.")
        return 1

    links = []
    for href in PDF_RE.findall(html):
        url = urljoin(PORTAL, href)
        host = urlparse(url).hostname or ""
        if host == "moe.gov.eg" or host.endswith(".moe.gov.eg"):
            if url not in links:
                links.append(url)

    if not links:
        print("No direct PDF links were discovered.")
        print("The Ministry page may render links dynamically or block automation.")
        print(f"Open manually: {PORTAL}")
        return 2

    print(f"Found {len(links)} Ministry PDF link(s).")
    for i, url in enumerate(links, start=1):
        name = Path(urlparse(url).path).name or f"grade3-{i}.pdf"
        dest = OUT / name
        try:
            data = fetch(url)
            dest.write_bytes(data)
            print(f"[{i}/{len(links)}] {dest}")
        except Exception as exc:
            print(f"[{i}/{len(links)}] FAILED {url}: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
