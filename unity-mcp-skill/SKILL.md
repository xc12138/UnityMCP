---
name: unity-mcp-orchestrator
description: 通过 MCP（Model Context Protocol）工具和资源编排 Unity Editor。适用于通过 MCP for Unity 操作 Unity 项目时：创建/修改 GameObject、编辑脚本、管理场景、运行测试，或任何 Unity 编辑器自动化场景。提供最佳实践、工具参数规范和工作流模式，帮助你高效集成 Unity-MCP。
---

# Unity-MCP 操作指南

这个 skill 帮助你更有效地使用 MCP 工具与资源操作 Unity Editor。

## 模板说明

`references/workflows.md` 和 `references/tools-reference.md` 中的示例是可复用模板。它们在不同 Unity 版本、包配置（UGUI/TMP/Input System）以及项目约定下可能并不完全准确。实现后请务必检查控制台、编译错误，或使用截图进行验证。

在套用模板前：
- 先通过资源和 `find_gameobjects` 校验目标对象/组件。
- 将名称、枚举值和属性 payload 视为占位符，按你的项目做适配。

## 快速开始：资源优先工作流

**在调用工具前，总是先读取相关资源。** 这样可以减少错误，并获得必要上下文。

```
1. 检查编辑器状态      → mcpforunity://editor/state
2. 理解当前场景        → mcpforunity://scene/gameobject-api
3. 查找目标对象/信息   → find_gameobjects 或 resources
4. 执行操作            → tools (manage_gameobject, create_script, script_apply_edits, apply_text_edits, validate_script, delete_script, get_sha 等)
5. 验证结果            → read_console, manage_camera(action="screenshot"), resources
```

## 关键最佳实践

### 1. 写入/编辑脚本后：等待编译并检查控制台

```python
# 在 create_script 或 script_apply_edits 之后：
# 这两个工具已自动触发 AssetDatabase.ImportAsset + RequestScriptCompilation。
# 不需要再调用 refresh_unity —— 只需等待编译结束，然后检查控制台。

# 1. 轮询编辑器状态直到编译完成
# 读取 mcpforunity://editor/state → 等待 is_compiling == false

# 2. 检查编译错误
read_console(types=["error"], count=10, include_stacktrace=True)
```

**原因：** Unity 必须先完成脚本编译，脚本才能被正常使用。`create_script` 和 `script_apply_edits` 已经自动触发导入与编译，随后再调 `refresh_unity` 是冗余的。

### 2. 多操作场景使用 `batch_execute`

```python
# 比串行逐个调用快 10-100 倍
batch_execute(
    commands=[
        {"tool": "manage_gameobject", "params": {"action": "create", "name": "Cube1", "primitive_type": "Cube"}},
        {"tool": "manage_gameobject", "params": {"action": "create", "name": "Cube2", "primitive_type": "Cube"}},
        {"tool": "manage_gameobject", "params": {"action": "create", "name": "Cube3", "primitive_type": "Cube"}}
    ],
    parallel=True  # 仅为提示：Unity 仍可能按顺序执行
)
```

**默认每批最多 25 条命令（可在 Unity MCP Tools 窗口中配置，最高 100）。** 若操作有依赖关系，使用 `fail_fast=True`。

**提示：** 发现阶段也可以用 `batch_execute` —— 把多个 `find_gameobjects` 放在一批里，而不是逐条调用：
```python
batch_execute(commands=[
    {"tool": "find_gameobjects", "params": {"search_term": "Camera", "search_method": "by_component"}},
    {"tool": "find_gameobjects", "params": {"search_term": "Player", "search_method": "by_tag"}},
    {"tool": "find_gameobjects", "params": {"search_term": "GameManager", "search_method": "by_name"}}
])
```

### 3. 用截图验证可视化结果

```python
# 基础截图（保存到 Assets/，仅返回文件路径）
manage_camera(action="screenshot")

# 内联截图（直接返回 base64 PNG 给 AI）
manage_camera(action="screenshot", include_image=True)

# 指定相机并限制分辨率，减小 payload
manage_camera(action="screenshot", camera="MainCamera", include_image=True, max_resolution=512)

# 环绕批量截图：前/后/左/右/顶/鸟瞰
manage_camera(action="screenshot", batch="surround", max_resolution=256)

# 以指定对象为中心的环绕截图
manage_camera(action="screenshot", batch="surround", view_target="Player", max_resolution=256)

# 定位截图：一次调用内临时摆放相机并拍摄
manage_camera(action="screenshot", view_target="Player", view_position=[0, 10, -10], max_resolution=512)

# Scene View 截图：捕获开发者在编辑器中看到的视图
manage_camera(action="screenshot", capture_source="scene_view", include_image=True)

# 在 Scene View 中聚焦某个对象
manage_camera(action="screenshot", capture_source="scene_view", view_target="Canvas", include_image=True)
```

**用于 AI 场景理解的最佳实践：**
- 当你需要“看见”场景而不只是保存文件时，使用 `include_image=True`。
- 使用 `batch="surround"` 快速获得全面视角（6 个角度，一条命令）。
- 用 `view_target`/`view_position` 从特定视角拍摄，无需依赖场景相机。
- 用 `capture_source="scene_view"` 查看编辑器视口（gizmos、线框、网格）。
- 将 `max_resolution` 控制在 256–512，平衡画质和 token 成本。

```python
# Agent 化相机循环：对准、拍摄、分析
manage_gameobject(action="look_at", target="MainCamera", look_at_target="Player")
manage_camera(action="screenshot", camera="MainCamera", include_image=True, max_resolution=512)
# → 分析图片，决定下一步动作

# 多视角截图（6 视角拼图）
manage_camera(action="screenshot_multiview", max_resolution=480)

# 用 Scene View 做编辑器级检查（显示 gizmo、调试覆盖层等）
manage_camera(action="screenshot", capture_source="scene_view", view_target="Player", include_image=True)
```

### 4. 重大改动后检查控制台

```python
read_console(
    action="get",
    types=["error", "warning"],  # 聚焦问题
    count=10,
    format="detailed"
)
```

### 5. 复杂操作前先看 `editor_state`

```python
# 读取 mcpforunity://editor/state 并检查：
# - is_compiling: 为 true 则等待
# - is_domain_reload_pending: 为 true 则等待
# - ready_for_tools: 仅在 true 时继续
# - blocking_reasons: 工具可能失败的原因
```

## 参数类型约定

以下是常见模式，不是严格保证。`manage_components.set_property` 的 payload 结构会因组件/属性而异；如果模板失败，请先检查组件资源返回的数据结构再调整。

### 向量（position, rotation, scale, color）
```python
# 两种形式都可接受：
position=[1.0, 2.0, 3.0]        # 列表
position="[1.0, 2.0, 3.0]"     # JSON 字符串
```

### 布尔值
```python
# 两种形式都可接受：
include_inactive=True           # Boolean
include_inactive="true"         # String
```

### 颜色
```python
# 自动识别格式：
color=[255, 0, 0, 255]         # 0-255 范围
color=[1.0, 0.0, 0.0, 1.0]    # 0.0-1.0 归一化（自动转换）
```

### 路径
```python
# 相对 Assets（默认）：
path="Assets/Scripts/MyScript.cs"

# URI 形式：
uri="mcpforunity://path/Assets/Scripts/MyScript.cs"
uri="file:///full/path/to/file.cs"
```

## 核心工具分类

| 分类 | 关键工具 | 用途 |
|------|----------|------|
| **Scene** | `manage_scene`, `find_gameobjects` | 场景操作、对象查找 |
| **Objects** | `manage_gameobject`, `manage_components` | 创建/修改 GameObject |
| **Scripts** | `create_script`, `script_apply_edits`, `validate_script` | C# 代码管理（创建/编辑后会自动刷新） |
| **Assets** | `manage_asset`, `manage_prefabs` | 资源操作。**Prefab 实例化应通过 `manage_gameobject(action="create", prefab_path="...")`，而不是 `manage_prefabs`。** |
| **Editor** | `manage_editor`, `execute_menu_item`, `read_console` | 编辑器控制、包部署（`deploy_package`/`restore_package`） |
| **Testing** | `run_tests`, `get_test_job` | Unity Test Framework |
| **Batch** | `batch_execute` | 并行/批量操作 |
| **Camera** | `manage_camera` | 相机管理（Unity Camera + Cinemachine）。**Tier 1（始终可用）**：create、target、lens、priority、list、screenshot。**Tier 2（需 `com.unity.cinemachine`）**：brain、body/aim/noise pipeline、extensions、blending、force/release。含 7 个预设：follow、third_person、freelook、dolly、static、top_down、side_scroller。资源：`mcpforunity://scene/cameras`。可用 `ping` 检查 Cinemachine 状态。见 [tools-reference.md](references/tools-reference.md#camera-tools)。 |
| **Graphics** | `manage_graphics` | 渲染与后处理管理。共 33 个 action，分 5 组：**Volume**（体积与效果，URP/HDRP）、**Bake**（光照贴图/光照探针/反射探针，仅 Edit 模式）、**Stats**（draw calls、batches、内存）、**Pipeline**（质量等级、管线设置）、**Features**（URP Renderer Feature：增删开关重排）。资源：`mcpforunity://scene/volumes`、`mcpforunity://rendering/stats`、`mcpforunity://pipeline/renderer-features`。可用 `ping` 检查管线状态。见 [tools-reference.md](references/tools-reference.md#graphics-tools)。 |
| **Packages** | `manage_packages` | 安装、移除、搜索、管理 Unity 包与 scoped registries。查询类 action：list installed、search registry、get info、ping、poll status。修改类 action：add/remove package、embed、add/remove scoped registry、force resolve。会校验标识符、提示 git URL 风险、移除前检查依赖（`force=true` 可覆盖）。见 [tools-reference.md](references/tools-reference.md#package-tools)。 |
| **ProBuilder** | `manage_probuilder` | 3D 建模、网格编辑、复杂几何。**安装 `com.unity.probuilder` 后，若需可编辑几何、多材质面或复杂形体，优先用 ProBuilder 形状而非 primitive GameObject。** 支持 12 种形状、面/边/点编辑、平滑、按面材质。见 [ProBuilder Guide](references/probuilder-guide.md)。 |
| **UI** | `manage_ui`, `batch_execute` with `manage_gameobject` + `manage_components` | **UI Toolkit**：用 `manage_ui` 创建 UXML/USS、挂载 UIDocument、检查可视树。**uGUI (Canvas)**：优先使用 TMP 方案（`TextMeshProUGUI`、`TMP_Dropdown`、`TMP_InputField`，以及 Button 子节点文本用 `TextMeshProUGUI`），避免 Legacy `Text/Dropdown/Input Field`。**先读 `mcpforunity://project/info` 判断 uGUI/TMP/Input System/UI Toolkit 可用性。**（见 [UI workflows](references/workflows.md#ui-creation-workflows)） |
| **Docs** | `unity_reflect`, `unity_docs` | API 校验与文档检索。**`unity_reflect`** 通过反射检查实时 C# API（需 Unity 连接）：`search` 跨程序集找类型，`get_type` 看成员摘要，`get_member` 看完整签名。**`unity_docs`** 拉取官方文档（不需 Unity 连接）：`get_doc`（ScriptReference）、`get_manual`（Manual）、`get_package_doc`（包文档）、`lookup`（并行搜索所有来源 + 项目资产）。**可信度层级：reflection > project assets > docs。** 推荐流程：`unity_reflect` search -> get_type -> get_member -> `unity_docs` lookup。见 [tools-reference.md](references/tools-reference.md#docs-tools)。 |

## 常见工作流

### 创建并使用新脚本

```python
# 1. 创建脚本（自动触发导入 + 编译）
create_script(
    path="Assets/Scripts/PlayerController.cs",
    contents="using UnityEngine;\n\npublic class PlayerController : MonoBehaviour\n{\n    void Update() { }\n}"
)

# 2. 等待编译完成
# 读取 mcpforunity://editor/state → 等待 is_compiling == false

# 3. 检查编译错误
read_console(types=["error"], count=10)

# 4. 然后再挂到 GameObject
manage_gameobject(action="modify", target="Player", components_to_add=["PlayerController"])
```

### 查找并修改 GameObject

```python
# 1. 按名称/标签/组件查找（只返回 ID）
result = find_gameobjects(search_term="Enemy", search_method="by_tag", page_size=50)

# 2. 通过资源拿完整数据
# mcpforunity://scene/gameobject/{instance_id}

# 3. 使用 ID 修改
manage_gameobject(action="modify", target=instance_id, position=[10, 0, 0])
```

### 运行并监控测试

```python
# 1. 启动测试（异步）
result = run_tests(mode="EditMode", test_names=["MyTests.TestSomething"])
job_id = result["job_id"]

# 2. 轮询直到完成
result = get_test_job(job_id=job_id, wait_timeout=60, include_failed_tests=True)
```

## 分页模式

大结果集会分页返回。务必跟进 `next_cursor`：

```python
cursor = 0
all_items = []
while True:
    result = manage_scene(action="get_hierarchy", page_size=50, cursor=cursor)
    all_items.extend(result["data"]["items"])
    if not result["data"].get("next_cursor"):
        break
    cursor = result["data"]["next_cursor"]
```

## 多实例工作流

当有多个 Unity Editor 同时运行时：

```python
# 1. 通过资源列出实例：mcpforunity://instances
# 2. 设置活跃实例
set_active_instance(instance="MyProject@abc123")
# 3. 之后所有调用都路由到该实例
```

## 错误恢复

| 现象 | 原因 | 解决方案 |
|------|------|----------|
| 工具返回 "busy" | 正在编译 | 等待并检查 `editor_state` |
| 出现 "stale_file" 错误 | 文件在 SHA 校验后发生变化 | 用 `get_sha` 重新获取 SHA 后重试 |
| 连接丢失 | 域重载（Domain Reload） | 等待约 5 秒后重连 |
| 命令无声失败 | 实例选错 | 检查 `set_active_instance` |

## 参考文件

查看更完整的参数与示例：

- **[tools-reference.md](references/tools-reference.md)**：完整工具文档与全部参数
- **[resources-reference.md](references/resources-reference.md)**：所有可用资源及其数据格式
- **[workflows.md](references/workflows.md)**：扩展工作流示例与模式
