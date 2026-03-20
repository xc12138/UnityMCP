#!/usr/bin/env python3
"""Translate only Markdown headings in workflows.md (outside fenced code blocks)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS_SRC = ROOT / "unity-mcp-skill" / "references" / "workflows.md"
WORKFLOWS_ZH = ROOT / "unity-mcp-skill" / "references" / "workflows-zh.md"

H1 = {"Unity-MCP Workflow Patterns": "Unity-MCP 工作流模式"}

H2_PLAIN = {
    "Table of Contents": "目录",
}

# (Chinese title, anchor id for <h2 id="...">)
H2_HTML: dict[str, tuple[str, str]] = {
    "Setup & Verification": ("设置与验证", "setup--verification"),
    "Scene Generator Build Workflow": ("场景生成器构建工作流", "scene-generator-build-workflow"),
    "Scene Creation Workflows": ("场景创建工作流", "scene-creation-workflows"),
    "Script Development Workflows": ("脚本开发工作流", "script-development-workflows"),
    "Asset Management Workflows": ("资源管理工作流", "asset-management-workflows"),
    "Testing Workflows": ("测试工作流", "testing-workflows"),
    "Debugging Workflows": ("调试工作流", "debugging-workflows"),
    "UI Creation Workflows": ("UI 创建工作流", "ui-creation-workflows"),
    "Input System: Old vs New": ("输入系统：旧版与新版", "input-system-old-vs-new"),
    "Camera & Cinemachine Workflows": ("相机与 Cinemachine 工作流", "camera--cinemachine-workflows"),
    "ProBuilder Workflows": ("ProBuilder 工作流", "probuilder-workflows"),
    "Graphics & Rendering Workflows": ("图形与渲染工作流", "graphics--rendering-workflows"),
    "Package Management Workflows": ("包管理工作流", "package-management-workflows"),
    "Package Deployment Workflows": ("包部署工作流", "package-deployment-workflows"),
    "API Verification Workflows": ("API 校验工作流", "api-verification-workflows"),
    "Batch Operations": ("批量操作", "batch-operations"),
    "Error Recovery Patterns": ("错误恢复模式", "error-recovery-patterns"),
}

H3: dict[str, str] = {
    "Initial Connection Verification": "初次连接验证",
    "Before Any Operation": "执行任何操作之前",
    "Fresh Scene Before Building": "构建前的全新场景",
    "Wiring Object References Between Components": "在组件之间连接对象引用",
    "Physics Requirements for Trigger-Based Interactions": "基于触发器交互的物理要求",
    "Script Overwrites with `manage_script(action=\"update\")`": "使用 `manage_script(action=\"update\")` 覆盖脚本",
    "Create Complete Scene from Scratch": "从零创建完整场景",
    "Populate Scene with Grid of Objects": "用对象网格填充场景",
    "Clone and Arrange Objects": "克隆并排列对象",
    "Create New Script and Attach": "创建新脚本并挂载",
    "Edit Existing Script Safely": "安全编辑现有脚本",
    "Add Method to Existing Class": "向现有类添加方法",
    "Create and Apply Material": "创建并应用材质",
    "Create Procedural Texture": "创建程序化纹理",
    "Organize Assets into Folders": "将资源整理到文件夹",
    "Search and Process Assets": "搜索并处理资源",
    "Instantiate Prefab in Scene": "在场景中实例化预制体",
    "Run Specific Tests": "运行指定测试",
    "Run Tests by Category": "按类别运行测试",
    "Test-Driven Development Pattern": "测试驱动开发模式",
    "Diagnose Compilation Errors": "诊断编译错误",
    "Investigate Missing References": "排查缺失引用",
    "Check Scene State": "检查场景状态",
    "Step 0: Detect Project UI Capabilities": "步骤 0：检测项目 UI 能力",
    "UI Toolkit Workflows (manage_ui)": "UI Toolkit 工作流（manage_ui）",
    "uGUI (Canvas-Based) Workflows": "uGUI（基于 Canvas）工作流",
    "RectTransform Sizing (Critical for All UI Children)": "RectTransform 尺寸（对所有 UI 子节点至关重要）",
    "Create Canvas (Foundation for All UI)": "创建 Canvas（所有 UI 的基础）",
    "Create EventSystem (Required Once Per Scene for UI Interaction)": "创建 EventSystem（每个场景仅需一次，用于 UI 交互）",
    "Create Panel (Background Container)": "创建 Panel（背景容器）",
    "Create Text (TextMeshPro)": "创建文本（TextMeshPro）",
    "Create Button (With Label)": "创建按钮（含标签）",
    "Create Slider (With Reference Wiring)": "创建滑块（含引用绑定）",
    "Create Input Field (With Reference Wiring)": "创建输入框（含引用绑定）",
    "Create Toggle (With Reference Wiring)": "创建开关（含引用绑定）",
    "Add Layout Group (Vertical/Horizontal/Grid)": "添加布局组（垂直/水平/网格）",
    "Complete Example: Main Menu Screen": "完整示例：主菜单界面",
    "UI Component Quick Reference": "UI 组件速查",
    "Detection": "检测",
    "EventSystem — Old Input Manager": "EventSystem — 旧版 Input Manager",
    "EventSystem — New Input System": "EventSystem — 新版 Input System",
    "When `activeInputHandler` is `\"Both\"`": "当 `activeInputHandler` 为 `\"Both\"` 时",
    "Setting Up a Third-Person Camera": "设置第三人称相机",
    "Multi-Camera Setup with Blending": "多相机与混合设置",
    "Camera Without Cinemachine": "无 Cinemachine 的相机",
    "Camera Inspection Workflow": "相机检查工作流",
    "Scene View Screenshot Workflow": "Scene 视图截图工作流",
    "ProBuilder vs Primitives Decision": "ProBuilder 与 Primitive 的选择",
    "Basic ProBuilder Scene Build": "基础 ProBuilder 场景搭建",
    "Edit-Verify Loop Pattern": "编辑-验证循环模式",
    "Known Limitations": "已知限制",
    "Setting Up Post-Processing": "设置后处理",
    "Adding a Full-Screen Effect via Renderer Features (URP)": "通过 Renderer Features 添加全屏效果（URP）",
    "Configuring Light Baking": "配置光照烘焙",
    "Install a Package and Verify": "安装包并验证",
    "Add OpenUPM Registry and Install Package": "添加 OpenUPM 注册表并安装包",
    "Safe Package Removal": "安全移除包",
    "Install from Git URL (e.g., NuGetForUnity)": "从 Git URL 安装（例如 NuGetForUnity）",
    "Iterative Development Loop (Edit → Deploy → Test)": "迭代开发循环（编辑 → 部署 → 测试）",
    "Rollback After Failed Deploy": "部署失败后的回滚",
    "Full API Verification Before Writing Code": "编写代码前的完整 API 校验",
    "Batch API Lookup": "批量 API 查询",
    "Finding Shaders and Materials in Project": "在项目中查找着色器与材质",
    "Manual and Package Documentation": "手册与包文档",
    "Verifying APIs Across Unity Versions": "跨 Unity 版本校验 API",
    "Batch Discovery (Multi-Search)": "批量发现（多条件搜索）",
    "Mass Property Update": "批量属性更新",
    "Mass Object Creation with Variations": "带变体的批量创建对象",
    "Cleanup Pattern": "清理模式",
    "Stale File Recovery": "陈旧文件恢复",
    "Domain Reload Recovery": "域重载恢复",
    "Compilation Block Recovery": "编译阻塞恢复",
}

H4: dict[str, str] = {
    "Create a Complete UI Screen": "创建完整 UI 界面",
    "Update Existing UI": "更新现有 UI",
    "Custom PanelSettings": "自定义 PanelSettings",
}

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def translate_toc_line(line: str) -> str | None:
    """Translate visible text in TOC links, keep anchor. Returns None if not a TOC line."""
    m = re.match(r"^(\s*-\s*)\[([^\]]+)\]\((#[^)]+)\)\s*$", line)
    if not m:
        return None
    prefix, _text, anchor = m.groups()
    toc_map = {
        "#setup--verification": "设置与验证",
        "#scene-creation-workflows": "场景创建工作流",
        "#script-development-workflows": "脚本开发工作流",
        "#asset-management-workflows": "资源管理工作流",
        "#testing-workflows": "测试工作流",
        "#debugging-workflows": "调试工作流",
        "#ui-creation-workflows": "UI 创建工作流",
        "#camera--cinemachine-workflows": "相机与 Cinemachine 工作流",
        "#probuilder-workflows": "ProBuilder 工作流",
        "#graphics--rendering-workflows": "图形与渲染工作流",
        "#package-management-workflows": "包管理工作流",
        "#package-deployment-workflows": "包部署工作流",
        "#api-verification-workflows": "API 校验工作流",
        "#batch-operations": "批量操作",
    }
    if anchor in toc_map:
        return f"{prefix}[{toc_map[anchor]}]({anchor})"
    return None


def main() -> None:
    """Read English workflows.md, write Chinese-heading copy to workflows-zh.md (does not modify source)."""
    text = WORKFLOWS_SRC.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    in_fence = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue

        if not in_fence and stripped.startswith("- [") and "](" in stripped:
            toc_done = translate_toc_line(line.rstrip("\n"))
            if toc_done is not None:
                out.append(toc_done + "\n")
                continue

        if not in_fence:
            m = HEADING_RE.match(line.rstrip("\n"))
            if m:
                hashes, title = m.group(1), m.group(2)
                level = len(hashes)
                if level == 1 and title in H1:
                    out.append(f"# {H1[title]}\n")
                    continue
                if level == 2 and title in H2_PLAIN:
                    out.append(f"## {H2_PLAIN[title]}\n")
                    continue
                if level == 2 and title in H2_HTML:
                    zh, hid = H2_HTML[title]
                    out.append(f'<h2 id="{hid}">{zh}</h2>\n')
                    continue
                if level == 3 and title in H3:
                    out.append(f"### {H3[title]}\n")
                    continue
                if level == 4 and title in H4:
                    out.append(f"#### {H4[title]}\n")
                    continue

        out.append(line)

    WORKFLOWS_ZH.write_text("".join(out), encoding="utf-8")
    print(f"Wrote {WORKFLOWS_ZH}")


if __name__ == "__main__":
    main()
