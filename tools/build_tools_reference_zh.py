#!/usr/bin/env python3
"""
Regenerate unity-mcp-skill/references/tools-reference-zh.md from tools-reference.md:
- Translate # / ## (as <h2 id> for stable anchors) and prose outside code fences.
- Keep ### tool names and all ``` code blocks identical to English source.
"""
from __future__ import annotations

import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "unity-mcp-skill/references/tools-reference.md"
DST = ROOT / "unity-mcp-skill/references/tools-reference-zh.md"

H1_ZH = "Unity-MCP 工具参考"

H2_MAP: dict[str, tuple[str, str]] = {
    "Table of Contents": ("目录", "table-of-contents"),
    "Project Info Resource": ("项目信息资源", "project-info-resource"),
    "Infrastructure Tools": ("基础设施工具", "infrastructure-tools"),
    "Scene Tools": ("场景工具", "scene-tools"),
    "GameObject Tools": ("游戏对象工具", "gameobject-tools"),
    "Script Tools": ("脚本工具", "script-tools"),
    "Asset Tools": ("资源工具", "asset-tools"),
    "Material & Shader Tools": ("材质与着色器工具", "material--shader-tools"),
    "UI Tools": ("UI 工具", "ui-tools"),
    "Editor Control Tools": ("编辑器控制工具", "editor-control-tools"),
    "Testing Tools": ("测试工具", "testing-tools"),
    "Search Tools": ("搜索工具", "search-tools"),
    "Custom Tools": ("自定义工具", "custom-tools"),
    "Camera Tools": ("相机工具", "camera-tools"),
    "Graphics Tools": ("图形工具", "graphics-tools"),
    "Package Tools": ("包管理工具", "package-tools"),
    "ProBuilder Tools": ("ProBuilder 工具", "probuilder-tools"),
    "Docs Tools": ("文档工具", "docs-tools"),
}

TOC_EN_TO_ZH = {
    "Infrastructure Tools": "基础设施工具",
    "Scene Tools": "场景工具",
    "GameObject Tools": "游戏对象工具",
    "Script Tools": "脚本工具",
    "Asset Tools": "资源工具",
    "Material & Shader Tools": "材质与着色器工具",
    "UI Tools": "UI 工具",
    "Editor Control Tools": "编辑器控制工具",
    "Testing Tools": "测试工具",
    "Camera Tools": "相机工具",
    "Graphics Tools": "图形工具",
    "Package Tools": "包管理工具",
    "ProBuilder Tools": "ProBuilder 工具",
    "Docs Tools": "文档工具",
}

# Fixed translations (avoid MT mangling links / terms)
STATIC: dict[str, str] = {
    "Complete reference for all MCP tools. Each tool includes parameters, types, and usage examples.":
        "所有 MCP 工具的完整参考。每个工具都包含参数、类型和使用示例。",
    "> **Template warning:** Examples in this file are skill templates and may be inaccurate for some Unity versions, packages, or project setups. Validate parameters and payload shapes against your active tool schema and runtime behavior.":
        "> **模板警告：** 本文件中的示例为技能模板，在不同 Unity 版本、包或项目配置下可能不准确。请结合当前工具 schema 与运行时行为核对参数与 payload 结构。",
    "Read `mcpforunity://project/info` to detect project capabilities before making assumptions about UI, input, or rendering setup.":
        "在对 UI、输入或渲染设置做出假设之前，请阅读 `mcpforunity://project/info` 以检测项目能力。",
}

URL_RE = re.compile(r"(https?://\S+|mcpforunity://\S+|file:///[^\s)]+)")
TOC_LINE_RE = re.compile(r"^(\s*-\s*)\[([^\]]+)\]\((#[^)]+)\)\s*$")


def protect_tokens(s: str) -> tuple[str, list[str]]:
    tokens: list[str] = []

    def repl(m: re.Match[str]) -> str:
        tokens.append(m.group(0))
        return f"⟦{len(tokens)-1}⟧"

    s = URL_RE.sub(repl, s)
    # inline code
    s = re.sub(r"`[^`]+`", repl, s)
    return s, tokens


def restore_tokens(s: str, tokens: list[str]) -> str:
    for i, t in enumerate(tokens):
        s = s.replace(f"⟦{i}⟧", t)
    return s


def translate_text(translator, cache: dict[str, str], text: str) -> str:
    text = text.rstrip("\n")
    if not text.strip():
        return text
    if text in STATIC:
        return STATIC[text]
    if text in cache:
        return cache[text]
    prot, toks = protect_tokens(text)
    try:
        out = translator.translate(prot)
    except Exception:
        time.sleep(0.8)
        try:
            out = translator.translate(prot)
        except Exception:
            out = text
            cache[text] = out
            return out
    out = restore_tokens(out, toks)
    cache[text] = out
    time.sleep(0.04)
    return out


def main() -> None:
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        raise SystemExit("pip install deep-translator") from None

    translator = GoogleTranslator(source="en", target="zh-CN")
    cache: dict[str, str] = {}

    lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)
    out: list[str] = []
    in_fence = False

    for line in lines:
        raw = line
        stripped = line.rstrip("\n")
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(raw)
            continue

        if in_fence:
            out.append(raw)
            continue

        if stripped == "":
            out.append(raw)
            continue

        if stripped == "---":
            out.append(raw)
            continue

        if stripped.startswith("# ") and not stripped.startswith("##"):
            out.append(f"# {H1_ZH}\n")
            continue

        if stripped.startswith("## "):
            title = stripped[3:].strip()
            if title in H2_MAP:
                zh, hid = H2_MAP[title]
                out.append(f'<h2 id="{hid}">{zh}</h2>\n')
            else:
                # fallback: keep English heading
                out.append(raw)
            continue

        if stripped.startswith("### "):
            out.append(raw)
            continue

        m = TOC_LINE_RE.match(stripped)
        if m:
            pre, en_label, anchor = m.groups()
            zh_label = TOC_EN_TO_ZH.get(en_label, translate_text(translator, cache, en_label))
            out.append(f"{pre}[{zh_label}]({anchor})\n")
            continue

        # Tables, blockquotes, bullets, prose
        out.append(translate_text(translator, cache, stripped) + "\n")

    DST.write_text("".join(out), encoding="utf-8")
    print(f"Wrote {DST} ({len(cache)} unique translated segments cached)")


if __name__ == "__main__":
    main()
