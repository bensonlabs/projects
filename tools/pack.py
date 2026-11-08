#!/usr/bin/env python3
"""Pack everything this repo publishes under /projects/, exactly as bensonlabs.org serves it.

    python3 tools/pack.py                    # build and check dist/projects/
    python3 tools/pack.py --version v1.2.0   # also write dist/projects-v1.2.0.tar.gz + .sha256

site/ mirrors /projects/ (the games come from bensonlabs/games, into /projects/games/). A
release contains:
- every file under site/, minus what a browser never needs: Markdown (except index.md pages,
  which Jekyll renders), Rust, TOML, TypeScript, shell scripts, lockfiles, package, card and
  metadata files, hidden files, and anything a folder's .publishignore lists (glob patterns);
- every section's page with its cards written in (tools/sections.py);
- .components-wrap.json: the pages the blog wraps in the site header.

The blog (bensonlabs/blog) downloads the release, checks its sha256, unpacks it into /projects/
and wraps the listed pages.
"""
from __future__ import annotations

import argparse
import fnmatch
import gzip
import hashlib
import io
import json
import re
import shutil
import sys
import tarfile
from pathlib import Path

import sections
from html_checks import Page

SITE = sections.SITE
DIST = sections.REPO_ROOT / "dist"
OUT = DIST / "projects"
WRAP_FILE = ".components-wrap.json"
MAX_FILE_BYTES = 750 * 1024
VERSION_RE = re.compile(r"v\d+\.\d+\.\d+")

NEVER_PUBLISHED_SUFFIXES = {".md", ".rs", ".toml", ".ts", ".tsx", ".sh", ".lock"}
NEVER_PUBLISHED_NAMES = {"package.json", "package-lock.json", "tsconfig.json", "card.json",
                         "section.json", "metadata.json"}
NEVER_PUBLISHED_DIRS = {"node_modules", "dist"}
PUBLISHED_MARKDOWN = {"index.md"}  # a page Jekyll renders: a guide, a write-up


def read_publishignore(folder: Path) -> list[str]:
    path = folder / ".publishignore"
    if not path.is_file():
        return []
    lines = (line.strip() for line in path.read_text(encoding="utf-8").splitlines())
    return [line for line in lines if line and not line.startswith("#")]


def publishable(folder: Path, path: Path, ignore: list[str]) -> bool:
    rel = path.relative_to(folder)
    if any(part.startswith(".") for part in rel.parts):
        return False
    if any(part in NEVER_PUBLISHED_DIRS for part in rel.parts[:-1]):
        return False
    if path.name in PUBLISHED_MARKDOWN:
        return True
    if path.suffix.lower() in NEVER_PUBLISHED_SUFFIXES or path.name in NEVER_PUBLISHED_NAMES:
        return False
    return not any(fnmatch.fnmatch(rel.as_posix(), pattern) for pattern in ignore)


def ignored(path: Path) -> bool:
    """Listed in a .publishignore of the file's folder or any folder above it inside site/."""
    folder = path.parent
    while True:
        rel = path.relative_to(folder).as_posix()
        if any(fnmatch.fnmatch(rel, pattern) for pattern in read_publishignore(folder)):
            return True
        if folder == SITE or SITE not in folder.parents:
            return False
        folder = folder.parent


def pack_site() -> None:
    for path in sorted(p for p in SITE.rglob("*") if p.is_file()):
        if publishable(SITE, path, []) and not ignored(path):
            target = OUT / path.relative_to(SITE)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)


def write_sections() -> int:
    count = 0
    for section in sections.sections():
        target = OUT / section.relative_to(SITE) / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(sections.render_section(section), encoding="utf-8", newline="\n")
        count += 1
    (OUT / WRAP_FILE).write_text(json.dumps(sections.wrapped_pages(None), indent=2) + "\n",
                                 encoding="utf-8", newline="\n")
    return count


def check() -> list[str]:
    """No file over the size limit, every wrapped page a whole document, every card a page."""
    errors = []
    for path in sorted(p for p in OUT.rglob("*") if p.is_file()):
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            errors.append(f"{path.relative_to(OUT).as_posix()}: {size // 1024} KB, over the "
                          f"{MAX_FILE_BYTES // 1024} KB limit for one file")
    wrap = OUT / WRAP_FILE
    for page in json.loads(wrap.read_text(encoding="utf-8")) if wrap.is_file() else []:
        target = OUT / page
        if not target.is_file():
            errors.append(f"{page}: listed to get the site header, but not packed")
        elif not {"head", "body"} <= Page(target.read_text(encoding="utf-8", errors="replace")).tags:
            errors.append(f"{page}: needs a <head> and a <body> to get the site header")
    for section in sections.sections():
        for item in sections.items(section):
            data = sections.read_card(item)
            if data.get("link") or str(data.get("listed", "yes")).lower() == "no":
                continue  # a card that leads elsewhere, or no card at all
            folder = OUT / item.relative_to(SITE)
            if not ((folder / "index.html").is_file() or (folder / "index.md").is_file()):
                errors.append(f"{item.relative_to(SITE).as_posix()}: its card leads to a page that isn't packed")
    return errors


def write_release(version: str) -> Path:
    """Pack OUT reproducibly (sorted entries, fixed times and modes): the same files
    always give the same sha256."""
    name = f"projects-{version}.tar.gz"
    files = sorted((p for p in OUT.rglob("*") if p.is_file()), key=lambda p: p.relative_to(OUT).as_posix())
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for path in files:
            info = tarfile.TarInfo(path.relative_to(OUT).as_posix())
            info.size = path.stat().st_size
            info.mode = 0o644
            info.mtime = 0
            with path.open("rb") as handle:
                tar.addfile(info, handle)
    archive = DIST / name
    with archive.open("wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
        gz.write(buffer.getvalue())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (DIST / f"{name}.sha256").write_text(f"{digest}  {name}\n", encoding="utf-8", newline="\n")
    return archive


def main() -> None:
    parser = argparse.ArgumentParser(description="Pack everything under /projects/ for bensonlabs.org.")
    parser.add_argument("--version", help="release version such as v1.2.0; also writes the release file")
    args = parser.parse_args()
    if args.version and not VERSION_RE.fullmatch(args.version):
        sys.exit(f"--version must look like v1.2.0, not {args.version!r}")

    if DIST.exists():
        shutil.rmtree(DIST)
    pack_site()
    section_count = write_sections()
    errors = check()
    if errors:
        print("Pack FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    files = [p for p in OUT.rglob("*") if p.is_file()]
    size = sum(p.stat().st_size for p in files)
    print(f"Packed {section_count} section pages: {len(files)} files, {size / 1048576:.1f} MB in dist/projects/")
    if args.version:
        archive = write_release(args.version)
        print((DIST / f"{archive.name}.sha256").read_text(encoding="utf-8").strip())


if __name__ == "__main__":
    main()
