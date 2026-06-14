#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "browser-profiles",
    "profiles",
    ".profiles",
    "runs",
    "run-artifacts",
}

BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".sqlite", ".sqlite3"}

PATTERNS = [
    ("private_key", re.compile("BEGIN [A-Z ]{0,32}PRIVATE KEY")),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{30,}")),
    ("openai_key", re.compile(r"sk-[A-Za-z0-9_-]{32,}")),
    ("generic_bearer", re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]{30,}")),
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("cookie_assignment", re.compile(r"(?i)\b(cookie|sessionid|session_id)\b\s*[:=]\s*['\"]?[A-Za-z0-9%._~+/=-]{20,}")),
]


def entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = {ch: text.count(ch) for ch in set(text)}
    return -sum((count / len(text)) * math.log2(count / len(text)) for count in counts.values())


def iter_files(root: Path):
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in BINARY_SUFFIXES:
            continue
        yield path


def scan_file(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    findings = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for name, pattern in PATTERNS:
            if pattern.search(line):
                findings.append((path, line_no, name, line.strip()[:180]))
        for token in re.findall(r"[A-Za-z0-9_./+=-]{48,}", line):
            if entropy(token) >= 4.2 and not token.startswith(("https://", "http://")):
                findings.append((path, line_no, "high_entropy_token", token[:80] + "..."))
    return findings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Generic secret scanner for this repository")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    findings = []
    for path in iter_files(root):
        findings.extend(scan_file(path))
    if findings:
        for path, line_no, name, preview in findings:
            rel = path.relative_to(root)
            print(f"{rel}:{line_no}: {name}: {preview}")
        return 1
    print("secret_scan: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
