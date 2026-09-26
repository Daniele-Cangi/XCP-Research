#!/usr/bin/env python3
"""Fail-closed publication hygiene audit for the public repository."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


TEXT_NAMES = {"LICENSE", ".gitignore"}
TEXT_SUFFIXES = {".md", ".py", ".json", ".svg", ".yml", ".yaml"}
SKIP_PARTS = {".git", "__pycache__", ".pytest_cache"}
# Exact public captures at the repository's recorded visual baseline. The
# Git blob ID binds the original bytes; SHA-256 and length make drift explicit.
PUBLIC_CAPTURES = {
    "assets/showcase/01-studio-workspace.webp": (29028, "0c3b1bda7185ec023f520212fc262f3ad57be9724004a05b9a12ae66c511155a", "b504178fc028796018a4bf496af470ac284c95f0"),
    "assets/showcase/02-core-siege.webp": (62184, "0db01f88bb9550a255383cc6bc3581cdd61b05050bd40bd8ceb55a82cec03844", "cc6498fb51667b3ab74ab0abbca6995d895f2eb4"),
    "assets/showcase/03-minilens.webp": (56188, "76a239e5e7b70a621860c5ecb38e65716485423adccaa87cb41d2f36c7c297a7", "9dadecc3d6356173e77dca88f7666cc8f830aa55"),
    "assets/showcase/04-studio-evidence.webp": (65992, "4e9749ee9984f3d0de81cb4a13b8a42e1a717cacacfa8b26324322512de2a995", "6e9476586c4cf1494f01a8c286ddc1c1a2a3f67e"),
    "assets/social-preview/xcp-research-github-social-preview.png": (83088, "0517e3d3dbe77a4ceb96bea4a50f09a93e54e923b4534d5afce41ad5a2658da5", "e35c483ca1939757b23801e61acbadca8c263257"),
}
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
    seen_captures: set[str] = set()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        name = relative.as_posix()
        if any(part in SKIP_PARTS for part in relative.parts):
            continue
        if name in PUBLIC_CAPTURES:
            seen_captures.add(name)
            if path.is_symlink() or not path.is_file():
                findings.append(f"{name}: public capture is missing or linked")
                continue
            data = path.read_bytes()
            expected_size, expected_sha256, expected_blob = PUBLIC_CAPTURES[name]
            blob = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
            if (len(data) != expected_size or hashlib.sha256(data).hexdigest() != expected_sha256
                    or blob != expected_blob):
                findings.append(f"{name}: public capture differs from pinned bytes")
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
    for missing in sorted(PUBLIC_CAPTURES.keys() - seen_captures):
        findings.append(f"{missing}: registered public capture is missing")
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
