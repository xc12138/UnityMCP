from pathlib import Path

p = Path(__file__).resolve().parents[1] / "unity-mcp-skill/references/tools-reference-zh.md"
lines = p.read_text(encoding="utf-8").splitlines()
in_fence = False
for i, line in enumerate(lines, 1):
    s = line.strip()
    if s.startswith("```"):
        in_fence = not in_fence
        continue
    if in_fence:
        continue
    if not s or s == "---":
        continue
    if s.startswith("#"):
        continue
    if s.startswith("|") or s.startswith("!["):
        continue
    if "`" in s and s.count("`") >= 2:
        continue
    letters = sum(1 for c in s if "a" <= c.lower() <= "z")
    if letters < len(s) * 0.35:
        continue
    if any("\u4e00" <= c <= "\u9fff" for c in s):
        continue
    print(f"{i}: {s[:120]}")
