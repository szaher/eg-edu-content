#!/usr/bin/env python3
"""Fetch Egyptian Ministry curriculum files for all school levels.

The Ministry e-library is the authoritative source, but its public site may return
403/blank responses for some clients. This fetcher therefore discovers the
currently indexed 2026/2027 curriculum through a reachable mirror index that
hosts Ministry-issued files for download.

Downloaded files are written under downloads/ and should not be committed.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

INDEX = "https://natega24.com/moe/index.html"
OUT_ROOT = Path("downloads")
HREF_RE = re.compile(r'''href=["']([^"']+)["']''', re.I)
ANCHOR_RE = re.compile(r'''<a\b[^>]*href=["']([^"']+)["'][^>]*>(.*?)</a>''', re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")

ARABIC_ORDINALS = {
    "الأول": 1,
    "الاول": 1,
    "الثاني": 2,
    "الثانى": 2,
    "الثالث": 3,
    "الرابع": 4,
    "الخامس": 5,
    "السادس": 6,
}


@dataclass(frozen=True)
class Level:
    slug: str
    title: str
    url: str


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


def text_of(raw_html: str) -> str:
    return WS_RE.sub(" ", html.unescape(TAG_RE.sub(" ", raw_html))).strip()


def anchors(page_url: str, body: bytes) -> list[tuple[str, str]]:
    text = body.decode("utf-8", errors="ignore")
    result: list[tuple[str, str]] = []
    for href, label in ANCHOR_RE.findall(text):
        result.append((urljoin(page_url, html.unescape(href)), text_of(label)))
    return result


def hrefs(page_url: str, body: bytes) -> list[str]:
    text = body.decode("utf-8", errors="ignore")
    return [urljoin(page_url, html.unescape(href)) for href in HREF_RE.findall(text)]


def ordinal_from_title(title: str) -> int | None:
    for word, number in ARABIC_ORDINALS.items():
        if word in title:
            return number
    return None


def level_slug(title: str) -> str | None:
    number = ordinal_from_title(title)
    if number is None:
        return None

    if "رياض الأطفال" in title or "رياض الاطفال" in title:
        return f"kg-{number}"
    if "تعليم مجتمعي" in title:
        return f"community-{number}"
    if "الابتدائي" in title or "الإبتدائي" in title:
        return f"primary-{number}"
    if "الإعدادي" in title or "الاعدادي" in title:
        return f"preparatory-{number}"
    if "الثانوي" in title or "الثانوى" in title:
        return f"secondary-{number}"
    return None


def discover_levels(index_body: bytes) -> list[Level]:
    discovered: dict[str, Level] = {}
    for url, title in anchors(INDEX, index_body):
        parsed = urlparse(url)
        if parsed.hostname != "natega24.com":
            continue
        if not parsed.path.startswith("/moe/moe-") or not parsed.path.endswith(".html"):
            continue
        slug = level_slug(title)
        if not slug:
            continue
        discovered[slug] = Level(slug=slug, title=title, url=url)

    stage_order = {"kg": 0, "primary": 1, "preparatory": 2, "secondary": 3, "community": 4}

    def sort_key(level: Level) -> tuple[int, int]:
        stage, number = level.slug.rsplit("-", 1)
        return stage_order.get(stage, 99), int(number)

    return sorted(discovered.values(), key=sort_key)


def is_subject_page(level_url: str, candidate: str) -> bool:
    level_path = unquote(urlparse(level_url).path)
    candidate_path = unquote(urlparse(candidate).path)
    if urlparse(candidate).hostname != "natega24.com":
        return False
    if not candidate_path.endswith(".html"):
        return False
    prefix = level_path[:-5] + "-"
    return candidate_path.startswith(prefix)


def is_pdf(url: str) -> bool:
    parsed = urlparse(url)
    return (
        parsed.hostname == "natega24.com"
        and parsed.path.startswith("/assets/moe/")
        and parsed.path.lower().endswith(".pdf")
    )


def safe_name(url: str, number: int) -> str:
    name = unquote(Path(urlparse(url).path).name)
    name = re.sub(r"[^\w.\-()\[\] \u0600-\u06ff]+", "_", name, flags=re.UNICODE)
    if not name:
        name = f"file-{number:04d}.pdf"
    return name


def discover_level_pdfs(level: Level) -> tuple[list[str], list[str]]:
    level_body = fetch(level.url)
    subject_pages = sorted({u for u in hrefs(level.url, level_body) if is_subject_page(level.url, u)})

    pdfs: set[str] = set()
    for page in subject_pages:
        try:
            body = fetch(page)
        except Exception as exc:
            print(f"WARN subject page failed: {page}: {exc}", file=sys.stderr)
            continue
        pdfs.update(u for u in hrefs(page, body) if is_pdf(u))

    return subject_pages, sorted(pdfs)


def write_manifest(level: Level, subject_pages: list[str], pdfs: list[str], out_dir: Path) -> None:
    manifest = {
        "academic_year": "2026/2027",
        "level": level.slug,
        "title": level.title,
        "index_url": INDEX,
        "level_url": level.url,
        "subject_pages": subject_pages,
        "pdfs": pdfs,
        "counts": {"subjects": len(subject_pages), "pdfs": len(pdfs)},
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def download_one(url: str, out_dir: Path, number: int, overwrite: bool) -> tuple[str, str]:
    name = safe_name(url, number)
    dest = out_dir / name
    if dest.exists() and not overwrite:
        return "skip", str(dest)

    data = fetch(url)
    if not data.startswith(b"%PDF"):
        raise ValueError("response is not a PDF")

    if dest.exists() and overwrite:
        dest.unlink()

    if dest.exists():
        suffix = hashlib.sha256(url.encode("utf-8")).hexdigest()[:10]
        dest = dest.with_name(f"{dest.stem}-{suffix}{dest.suffix}")

    dest.write_bytes(data)
    return "download", str(dest)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--level",
        action="append",
        default=[],
        help=(
            "Level slug to fetch, e.g. primary-3 or secondary-2. "
            "Repeat for multiple levels. Omit or use 'all' for every discovered level."
        ),
    )
    parser.add_argument(
        "--mainstream-only",
        action="store_true",
        help="Exclude community-education levels; fetch KG, primary, preparatory and secondary only.",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Discover sources and write manifests without downloading PDFs.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Parallel PDF downloads per level (default: 4).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-download files that already exist.",
    )
    parser.add_argument(
        "--list-levels",
        action="store_true",
        help="Print discovered level slugs and exit.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.workers < 1 or args.workers > 16:
        print("--workers must be between 1 and 16", file=sys.stderr)
        return 2

    try:
        index_body = fetch(INDEX)
    except Exception as exc:
        print(f"Could not read curriculum index: {exc}", file=sys.stderr)
        print(f"Open manually: {INDEX}", file=sys.stderr)
        return 1

    levels = discover_levels(index_body)
    if args.mainstream_only:
        levels = [level for level in levels if not level.slug.startswith("community-")]

    if not levels:
        print("No curriculum levels were discovered.", file=sys.stderr)
        return 3

    if args.list_levels:
        for level in levels:
            print(f"{level.slug:16} {level.title}  {level.url}")
        return 0

    requested = {item for item in args.level if item != "all"}
    if requested:
        available = {level.slug for level in levels}
        missing = sorted(requested - available)
        if missing:
            print(f"Unknown level(s): {', '.join(missing)}", file=sys.stderr)
            print(f"Available: {', '.join(sorted(available))}", file=sys.stderr)
            return 2
        levels = [level for level in levels if level.slug in requested]

    print(f"Discovered {len(levels)} curriculum level(s).")
    total_pdfs = 0
    downloaded = 0
    skipped = 0
    failed = 0

    for level in levels:
        print(f"\n== {level.slug}: {level.title} ==")
        try:
            subject_pages, pdfs = discover_level_pdfs(level)
        except Exception as exc:
            print(f"FAILED to discover {level.slug}: {exc}", file=sys.stderr)
            failed += 1
            continue

        out_dir = OUT_ROOT / level.slug
        write_manifest(level, subject_pages, pdfs, out_dir)
        total_pdfs += len(pdfs)
        print(f"Found {len(subject_pages)} subject page(s), {len(pdfs)} PDF(s).")

        if args.manifest_only:
            continue

        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {
                pool.submit(download_one, url, out_dir, i, args.overwrite): url
                for i, url in enumerate(pdfs, start=1)
            }
            for future in as_completed(futures):
                url = futures[future]
                try:
                    status, path = future.result()
                    if status == "download":
                        downloaded += 1
                        print(f"DOWNLOADED {path}")
                    else:
                        skipped += 1
                        print(f"SKIP {path}")
                except Exception as exc:
                    failed += 1
                    print(f"FAILED {url}: {exc}", file=sys.stderr)

    print("\nSummary")
    print(f"  levels:     {len(levels)}")
    print(f"  PDFs found: {total_pdfs}")
    if not args.manifest_only:
        print(f"  downloaded: {downloaded}")
        print(f"  skipped:    {skipped}")
        print(f"  failed:     {failed}")

    return 0 if failed == 0 else 4


if __name__ == "__main__":
    raise SystemExit(main())
