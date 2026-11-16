"""Audit script checking forbidden vocabulary, forbidden design tokens, punctuation, and emoji."""
from __future__ import annotations

import re
from pathlib import Path

FORBIDDEN_WORDS = [
    "delve", "dive in", "deep dive", "unlock", "unleash", "harness", "leverage",
    "empower", "elevate", "supercharge", "streamline", "seamless", "seamlessly",
    "robust", "cutting-edge", "state-of-the-art", "game-changing", "revolutionary",
    "transformative", "groundbreaking", "next-generation", "holistic", "synergy",
    "ecosystem", "landscape", "tapestry", "realm", "journey", "navigate", "embark",
    "foster", "crucial", "pivotal", "vital", "paramount", "meticulous", "intricate",
    "nuanced", "comprehensive", "tailored", "curated", "effortless", "effortlessly",
    "intuitive", "powerful", "smart", "ai-powered", "ai-driven", "at your fingertips",
    "take your", "in today's fast-paced world", "whether you're a", "look no further",
    "it's important to note", "it's worth noting", "that said", "ultimately",
    "in conclusion", "moreover", "furthermore"
]

FORBIDDEN_DESIGN = [
    "gradient", "radial-gradient", "linear-gradient", "backdrop-filter", "blur(",
    "box-shadow", "drop-shadow"
]


def audit():
    repo_root = Path(__file__).resolve().parent.parent.parent
    files_to_check = [
        repo_root / "frontend" / "content" / "strings.ts",
        repo_root / "frontend" / "content" / "about.ts",
    ]

    css_files = [
        repo_root / "frontend" / "src" / "index.css",
    ]

    errors = []

    for fpath in files_to_check:
        if not fpath.exists():
            continue
        text = fpath.read_text(encoding="utf-8")
        # Remove comments
        lines = [line for line in text.splitlines() if not line.strip().startswith("//") and not line.strip().startswith("*")]
        clean_text = "\n".join(lines)

        for w in FORBIDDEN_WORDS:
            pattern = r"\b" + re.escape(w) + r"\b"
            if re.search(pattern, clean_text, re.IGNORECASE):
                errors.append(f"Forbidden word '{w}' found in {fpath.name}")

        if "—" in clean_text:
            errors.append(f"Em dash '—' found in {fpath.name}")
        if "…" in clean_text:
            errors.append(f"Ellipsis '…' found in {fpath.name}")

        emoji_pattern = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)
        if emoji_pattern.search(clean_text):
            errors.append(f"Emoji found in {fpath.name}")

    for css_path in css_files:
        if not css_path.exists():
            continue
        css_text = css_path.read_text(encoding="utf-8")
        for token in FORBIDDEN_DESIGN:
            if token in css_text:
                errors.append(f"Forbidden design token '{token}' found in {css_path.name}")

    if errors:
        print("AUDIT FAILED:")
        for err in errors:
            print(" -", err)
        return False
    else:
        print("AUDIT PASSED: Zero forbidden words, zero em dashes, zero ellipses, zero emojis, zero forbidden design tokens.")
        return True


if __name__ == "__main__":
    import sys
    success = audit()
    sys.exit(0 if success else 1)
