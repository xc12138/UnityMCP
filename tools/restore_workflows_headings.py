#!/usr/bin/env python3
"""Restore English headings in workflows.md from the Chinese-heading variant (inverse of translate_workflows_headings)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))
import translate_workflows_headings as t  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / "unity-mcp-skill" / "references" / "workflows.md"

H1_INV = {v: k for k, v in t.H1.items()}
H2_PLAIN_INV = {v: k for k, v in t.H2_PLAIN.items()}
H2_ID_TO_EN = {v[1]: k for k, v in t.H2_HTML.items()}
H3_INV = {v: k for k, v in t.H3.items()}
H4_INV = {v: k for k, v in t.H4.items()}

TOC_ANCHOR_TO_EN = {
    "#setup--verification": "Setup & Verification",
    "#scene-creation-workflows": "Scene Creation Workflows",
    "#script-development-workflows": "Script Development Workflows",
    "#asset-management-workflows": "Asset Management Workflows",
    "#testing-workflows": "Testing Workflows",
    "#debugging-workflows": "Debugging Workflows",
    "#ui-creation-workflows": "UI Creation Workflows",
    "#camera--cinemachine-workflows": "Camera & Cinemachine Workflows",
    "#probuilder-workflows": "ProBuilder Workflows",
    "#graphics--rendering-workflows": "Graphics & Rendering Workflows",
    "#package-management-workflows": "Package Management Workflows",
    "#package-deployment-workflows": "Package Deployment Workflows",
    "#api-verification-workflows": "API Verification Workflows",
    "#batch-operations": "Batch Operations",
}

H2_TAG_RE = re.compile(r'^<h2 id="([^"]+)">[^<]*</h2>\s*$')


def restore_toc_line(line: str) -> str | None:
    m = re.match(r"^(\s*-\s*)\[([^\]]+)\]\((#[^)]+)\)\s*$", line)
    if not m:
        return None
    prefix, _text, anchor = m.groups()
    if anchor in TOC_ANCHOR_TO_EN:
        return f"{prefix}[{TOC_ANCHOR_TO_EN[anchor]}]({anchor})"
    return None


def main() -> None:
    lines = WORKFLOWS.read_text(encoding="utf-8").splitlines(keepends=True)
    out: list[str] = []
    in_fence = False
    head_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue

        if not in_fence and stripped.startswith("- [") and "](" in stripped:
            r = restore_toc_line(line.rstrip("\n"))
            if r is not None:
                out.append(r + "\n")
                continue

        if not in_fence:
            h2m = H2_TAG_RE.match(line.rstrip("\n"))
            if h2m:
                hid = h2m.group(1)
                if hid in H2_ID_TO_EN:
                    out.append(f"## {H2_ID_TO_EN[hid]}\n")
                    continue

            m = head_re.match(line.rstrip("\n"))
            if m:
                level = len(m.group(1))
                title = m.group(2)
                if level == 1 and title in H1_INV:
                    out.append(f"# {H1_INV[title]}\n")
                    continue
                if level == 2 and title in H2_PLAIN_INV:
                    out.append(f"## {H2_PLAIN_INV[title]}\n")
                    continue
                if level == 3 and title in H3_INV:
                    out.append(f"### {H3_INV[title]}\n")
                    continue
                if level == 4 and title in H4_INV:
                    out.append(f"#### {H4_INV[title]}\n")
                    continue

        out.append(line)

    WORKFLOWS.write_text("".join(out), encoding="utf-8")
    print(f"Restored English headings in {WORKFLOWS}")


if __name__ == "__main__":
    main()
