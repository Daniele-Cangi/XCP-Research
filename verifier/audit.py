#!/usr/bin/env python3
"""Fail-closed publication hygiene audit for the public repository."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


TEXT_NAMES = {"LICENSE", ".gitignore"}
TEXT_SUFFIXES = {".md", ".py", ".json", ".svg", ".yml", ".yaml"}
SKIP_PARTS = {".git", "__pycache__", ".pytest_cache"}
PATTERNS = [
    ("Windows absolute path", re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/][^\s\"']+")),
    ("home-directory path", re.compile(r"/(?:home|Users)/[^/\s]+", re.IGNORECASE)),
    ("cloud-synced local path", re.compile("One" + "Drive", re.IGNORECASE)),
    ("IP address", re.compile(r"(?<![0-9])(?:25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])){3}(?![0-9])")),
    ("local endpoint", re.compile(r"\b(?:local" + r"host|127\.0\.0\.1|0\.0\.0\.0)(?::[0-9]+)?\b", re.IGNORECASE)),
    ("authorization header", re.compile(r"\bauthorization\s*:\s*\S+", re.IGNORECASE)),
    ("bearer or basic credential", re.compile(r"\b(?:bearer|basic)\s+[A-Za-z0-9._~+/=-]{12,}", re.IGNORECASE)),
    ("credential assignment", re.compile(r"\b(?:password|passwd|token|secret|pairing[_ -]?(?:code|pin)|pin)\s*[:=]\s*[\"']?[^\s\"']{4,}", re.IGNORECASE)),
    ("session identifier assignment", re.compile(r"\bsession[_ -]?id\s*[:=]\s*[\"']?[A-Za-z0-9._-]{6,}", re.IGNORECASE)),
    ("private key block", re.compile("BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY")),
    ("certificate block", re.compile("BEGIN CERT" + "IFICATE")),
]


def audit(root: Path) -> tuple[int, list[str]]:
    root = root.resolve()
    findings: list[str] = []
    count = 0
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in SKIP_PARTS for part in relative.parts):
            continue
        if path.is_symlink():
            findings.append(f"{relative.as_posix()}: symlink is forbidden")
            continue
        if not path.is_file():
            continue
        if path.name not in TEXT_NAMES and path.suffix.lower() not in TEXT_SUFFIXES:
            findings.append(f"{relative.as_posix()}: non-text file type is forbidden")
            continue
        count += 1
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            findings.append(f"{relative.as_posix()}: cannot read as UTF-8 text: {exc}")
            continue
        if "\x00" in text:
            findings.append(f"{relative.as_posix()}: NUL byte is forbidden")
            continue
        for label, pattern in PATTERNS:
            match = pattern.search(text)
            if match:
                line = text.count("\n", 0, match.start()) + 1
                findings.append(f"{relative.as_posix()}:{line}: {label}")
    return count, findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    count, findings = audit(args.root)
    if findings:
        print("Publication audit ............ FAIL", file=sys.stderr)
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return 1
    print(f"Publication audit ............ PASS ({count} text files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
