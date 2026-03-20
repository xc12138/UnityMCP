# Unity-MCP 工具参考

MCP 全部工具的完整参考。每个工具都包含参数、类型和使用示例。

> **模板警告：** 本文件中的示例属于技能模板，在某些 Unity 版本、包组合或项目配置下可能不准确。请基于当前生效的工具 schema 与运行时行为校验参数和 payload 结构。

## 目录

- [基础设施工具](#infrastructure-tools)
- [场景工具](#scene-tools)
- [GameObject 工具](#gameobject-tools)
- [脚本工具](#script-tools)
- [资源工具](#asset-tools)
- [材质与 Shader 工具](#material--shader-tools)
- [UI 工具](#ui-tools)
- [编辑器控制工具](#editor-control-tools)
- [测试工具](#testing-tools)
- [相机工具](#camera-tools)
- [图形工具](#graphics-tools)
- [包管理工具](#package-tools)
- [ProBuilder 工具](#probuilder-tools)
- [文档工具](#docs-tools)

---

## 项目信息资源

在对 UI、输入系统或渲染配置做任何假设前，请先读取 `mcpforunity://project/info` 以识别项目能力。

**返回字段：**

| 字段 | 类型 | 说明 |
|-------|------|-------------|
| `projectRoot` | string | 项目根目录的绝对路径 |
| `projectName` | string | 项目文件夹名称 |
| `unityVersion` | string | 例如 `"2022.3.20f1"` |
| `platform` | string | 当前构建目标，例如 `"StandaloneWindows64"` |
| `assetsPath` | string | Assets 文件夹的绝对路径 |
| `renderPipeline` | string | `"BuiltIn"`、`"Universal"`、`"HighDefinition"` 或 `"Custom"` |
| `activeInputHandler` | string | `"Old"`、`"New"` 或 `"Both"` |
| `packages.ugui` | bool | 是否安装 `com.unity.ugui`（Canvas、Image、Button 等） |
| `packages.textmeshpro` | bool | 是否安装 `com.unity.textmeshpro`（TMP_Text、TMP_InputField） |
| `packages.inputsystem` | bool | 是否安装 `com.unity.inputsystem`（InputAction、PlayerInput） |
| `packages.uiToolkit` | bool | Unity 2021.3+ 恒为 `true`（UIDocument、VisualElement、UXML/USS） |
| `packages.screenCapture` | bool | 是否启用 `com.unity.modules.screencapture`（用于截图的 ScreenCapture API） |

**关键决策点：**

- **UI 系统**：若 `packages.uiToolkit` 为 true（Unity 2021+ 恒为 true），使用 `manage_ui` 进行 UI Toolkit 工作流（UXML/USS）。若 `packages.ugui` 为 true，则通过 `batch_execute` 使用 Canvas + uGUI 组件。新 UI 优先推荐 UI Toolkit，其流程更接近前端开发（UXML 负责结构，USS 负责样式）。
- **文本**：若 `packages.textmeshpro` 为 true，优先使用 `TextMeshProUGUI`，而不是旧版 `Text`。
- **输入**：根据 `activeInputHandler` 选择 EventSystem 模块——`StandaloneInputModule`（Old）或 `InputSystemUIInputModule`（New）。参见 [workflows.md — Input System](workflows.md#input-system-old-vs-new)。
- **Shader**：根据 `renderPipeline` 选择正确 shader 名称——`Standard`（BuiltIn）、`Universal Render Pipeline/Lit`（URP）或 `HDRP/Lit`（HDRP）。

---

## 基础设施工具

### batch_execute

在单个批次中执行多个 MCP 命令（速度可提升 10-100 倍）。

```python
batch_execute(
    commands=[                    # list[dict], required, max 25
        {"tool": "tool_name", "params": {...}},
        ...
    ],
    parallel=False,              # bool, optional - advisory only (Unity may still run sequentially)
    fail_fast=False,             # bool, optional - stop on first failure
    max_parallelism=None         # int, optional - max parallel workers
)
```

`batch_execute` 不是事务性的：后续命令失败时，前面成功的命令不会自动回滚。

### set_active_instance

将命令路由到指定 Unity 实例（适用于多实例工作流）。

```python
set_active_instance(
    instance="ProjectName@abc123"  # str, required - Name@hash or hash prefix
)
```

### refresh_unity

刷新资源数据库并触发脚本编译。

```python
refresh_unity(
    mode="if_dirty",             # "if_dirty" | "force"
    scope="all",                 # "assets" | "scripts" | "all"
    compile="none",              # "none" | "request"
    wait_for_ready=True          # bool - wait until editor ready
)
```

---

## 场景工具

### manage_scene

场景的 CRUD 操作、层级查询、截图与 Scene 视图控制。

```python
# Get hierarchy (paginated)
manage_scene(
    action="get_hierarchy",
    page_size=50,                # int, default 50, max 500
    cursor=0,                    # int, pagination cursor
    parent=None,                 # str|int, optional - filter by parent
    include_transform=False      # bool - include local transforms
)

# Screenshot (file only — saves to Assets/Screenshots/)
manage_camera(action="screenshot")

# Screenshot with inline image (base64 PNG returned to AI)
manage_scene(
    action="screenshot",
    camera="MainCamera",         # str, optional - camera name, path, or instance ID
    include_image=True,          # bool, default False - return base64 PNG inline
    max_resolution=512           # int, optional - downscale cap (default 640)
)

# Batch surround — contact sheet of 6 fixed angles (front/back/left/right/top/bird_eye)
manage_scene(
    action="screenshot",
    batch="surround",            # str - "surround" for 6-angle contact sheet
    max_resolution=256           # int - per-tile resolution cap
)
# Returns: single composite contact sheet image with labeled tiles

# Batch surround centered on a specific target
manage_scene(
    action="screenshot",
    batch="surround",
    view_target="Player",        # str|int|list[float] - center surround on this target
    max_resolution=256
)

# Batch orbit — configurable multi-angle grid around a target
manage_scene(
    action="screenshot",
    batch="orbit",               # str - "orbit" for configurable angle grid
    view_target="Player",        # str|int|list[float] - target to orbit around
    orbit_angles=8,              # int, default 8 - number of azimuth steps
    orbit_elevations=[0, 30],    # list[float], default [0, 30, -15] - vertical angles in degrees
    orbit_distance=10,           # float, optional - camera distance (auto-fit if omitted)
    orbit_fov=60,                # float, default 60 - camera FOV in degrees
    max_resolution=256           # int - per-tile resolution cap
)
# Returns: single composite contact sheet (angles × elevations tiles in a grid)

# Positioned screenshot (temp camera at viewpoint, no file saved)
manage_scene(
    action="screenshot",
    view_target="Enemy",         # str|int|list[float] - target to aim at
    view_position=[0, 10, -10],  # list[float], optional - camera position
    view_rotation=[45, 0, 0],    # list[float], optional - euler angles (overrides view_target aim)
    max_resolution=512
)

# Frame scene view on target
manage_scene(
    action="scene_view_frame",
    scene_view_target="Player"   # str|int - GO name, path, or instance ID to frame
)

# Other actions
manage_scene(action="get_active")        # Current scene info
manage_scene(action="get_build_settings") # Build settings
manage_scene(action="create", name="NewScene", path="Assets/Scenes/")
manage_scene(action="load", path="Assets/Scenes/Main.unity")
manage_scene(action="save")
```

### find_gameobjects

搜索 GameObject（仅返回实例 ID）。

```python
find_gameobjects(
    search_term="Player",        # str, required
    search_method="by_name",     # "by_name"|"by_tag"|"by_layer"|"by_component"|"by_path"|"by_id"
    include_inactive=False,      # bool|str
    page_size=50,                # int, default 50, max 500
    cursor=0                     # int, pagination cursor
)
# Returns: {"ids": [12345, 67890], "next_cursor": 50, ...}
```

---

## GameObject 工具

### manage_gameobject

创建、修改、删除、复制 GameObject。

```python
# Create
manage_gameobject(
    action="create",
    name="MyCube",               # str, required
    primitive_type="Cube",       # "Cube"|"Sphere"|"Capsule"|"Cylinder"|"Plane"|"Quad"
    position=[0, 1, 0],          # list[float] or JSON string "[0,1,0]"
    rotation=[0, 45, 0],         # euler angles
    scale=[1, 1, 1],
    components_to_add=["Rigidbody", "BoxCollider"],
    save_as_prefab=False,
    prefab_path="Assets/Prefabs/MyCube.prefab"
)

# Prefab instantiation — place a prefab instance in the scene
manage_gameobject(
    action="create",
    name="Enemy_1",
    prefab_path="Assets/Prefabs/Enemy.prefab",
    position=[5, 0, 3],
    parent="Enemies"                # optional parent GameObject
)
# Smart lookup — just the prefab name works too:
manage_gameobject(action="create", name="Enemy_2", prefab_path="Enemy", position=[10, 0, 3])

# Modify
manage_gameobject(
    action="modify",
    target="Player",             # name, path, or instance ID
    search_method="by_name",     # how to find target
    position=[10, 0, 0],
    rotation=[0, 90, 0],
    scale=[2, 2, 2],
    set_active=True,
    layer="Player",
    components_to_add=["AudioSource"],
    components_to_remove=["OldComponent"],
    component_properties={       # nested dict for property setting
        "Rigidbody": {
            "mass": 10.0,
            "useGravity": True
        }
    }
)

# Delete
manage_gameobject(action="delete", target="OldObject")

# Duplicate
manage_gameobject(
    action="duplicate",
    target="Player",
    new_name="Player2",
    offset=[5, 0, 0]             # position offset from original
)

# Move relative
manage_gameobject(
    action="move_relative",
    target="Player",
    reference_object="Enemy",    # optional reference
    direction="left",            # "left"|"right"|"up"|"down"|"forward"|"back"
    distance=5.0,
    world_space=True
)

# Look at target (rotates GO to face a point or another GO)
manage_gameobject(
    action="look_at",
    target="MainCamera",         # the GO to rotate
    look_at_target="Player",     # str (GO name/path) or list[float] world position
    look_at_up=[0, 1, 0]        # optional up vector, default [0,1,0]
)
```

### manage_components

对组件进行添加、移除或属性设置。

```python
# Add component
manage_components(
    action="add",
    target=12345,                # instance ID (preferred) or name
    component_type="Rigidbody",
    search_method="by_id"
)

# Remove component
manage_components(
    action="remove",
    target="Player",
    component_type="OldScript"
)

# Set single property
manage_components(
    action="set_property",
    target=12345,
    component_type="Rigidbody",
    property="mass",
    value=5.0
)

# Set multiple properties
manage_components(
    action="set_property",
    target=12345,
    component_type="Transform",
    properties={
        "position": [1, 2, 3],
        "localScale": [2, 2, 2]
    }
)

# Set object reference property (reference another GameObject by name)
manage_components(
    action="set_property",
    target="GameManager",
    component_type="GameManagerScript",
    property="targetObjects",
    value=[{"name": "Flower_1"}, {"name": "Flower_2"}, {"name": "Bee_1"}]
)

# Object reference formats supported:
# - {"name": "ObjectName"}     → Find GameObject in scene by name
# - {"instanceID": 12345}      → Direct instance ID reference
# - {"guid": "abc123..."}      → Asset GUID reference
# - {"path": "Assets/..."}     → Asset path reference
# - "Assets/Prefabs/My.prefab" → String shorthand for asset paths
# - "ObjectName"               → String shorthand for scene name lookup
# - 12345                      → Integer shorthand for instanceID
```

---

## 脚本工具

### create_script

创建新的 C# 脚本。

```python
create_script(
    path="Assets/Scripts/MyScript.cs",  # str, required
    contents='''using UnityEngine;

public class MyScript : MonoBehaviour
{
    void Start() { }
    void Update() { }
}''',
    script_type="MonoBehaviour",  # optional hint
    namespace="MyGame"            # optional namespace
)
```

### script_apply_edits

对 C# 脚本应用结构化编辑（比纯文本替换更安全）。

```python
script_apply_edits(
    name="MyScript",             # script name (no .cs)
    path="Assets/Scripts",       # folder path
    edits=[
        # Replace entire method
        {
            "op": "replace_method",
            "methodName": "Update",
            "replacement": "void Update() { transform.Rotate(Vector3.up); }"
        },
        # Insert new method
        {
            "op": "insert_method",
            "afterMethod": "Start",
            "code": "void OnEnable() { Debug.Log(\"Enabled\"); }"
        },
        # Delete method
        {
            "op": "delete_method",
            "methodName": "OldMethod"
        },
        # Anchor-based insert
        {
            "op": "anchor_insert",
            "anchor": "void Start()",
            "position": "before",  # "before" | "after"
            "text": "// Called before Start\n"
        },
        # Regex replace
        {
            "op": "regex_replace",
            "pattern": "Debug\\.Log\\(",
            "text": "Debug.LogWarning("
        },
        # Prepend/append to file
        {"op": "prepend", "text": "// File header\n"},
        {"op": "append", "text": "\n// File footer"}
    ]
)
```

### apply_text_edits

按精确字符位置应用编辑（行列均从 1 开始计数）。

```python
apply_text_edits(
    uri="mcpforunity://path/Assets/Scripts/MyScript.cs",
    edits=[
        {
            "startLine": 10,
            "startCol": 5,
            "endLine": 10,
            "endCol": 20,
            "newText": "replacement text"
        }
    ],
    precondition_sha256="abc123...",  # optional, prevents stale edits
    strict=True                        # optional, stricter validation
)
```

### validate_script

检查脚本的语法/语义错误。

```python
validate_script(
    uri="mcpforunity://path/Assets/Scripts/MyScript.cs",
    level="standard",            # "basic" | "standard"
    include_diagnostics=True     # include full error details
)
```

### get_sha

获取文件哈希而不返回内容（用于前置条件校验）。

```python
get_sha(uri="mcpforunity://path/Assets/Scripts/MyScript.cs")
# Returns: {"sha256": "...", "lengthBytes": 1234, "lastModifiedUtc": "..."}
```

### delete_script

删除脚本文件。

```python
delete_script(uri="mcpforunity://path/Assets/Scripts/OldScript.cs")
```

---

## 资源工具

### manage_asset

资源操作：搜索、导入、创建、修改、删除。

```python
# Search assets (paginated)
manage_asset(
    action="search",
    path="Assets",               # search scope
    search_pattern="*.prefab",   # glob or "t:MonoScript" filter
    filter_type="Prefab",        # optional type filter
    page_size=25,                # keep small to avoid large payloads
    page_number=1,               # 1-based
    generate_preview=False       # avoid base64 bloat
)

# Get asset info
manage_asset(action="get_info", path="Assets/Prefabs/Player.prefab")

# Create asset
manage_asset(
    action="create",
    path="Assets/Materials/NewMaterial.mat",
    asset_type="Material",
    properties={"color": [1, 0, 0, 1]}
)

# Duplicate/move/rename
manage_asset(action="duplicate", path="Assets/A.prefab", destination="Assets/B.prefab")
manage_asset(action="move", path="Assets/A.prefab", destination="Assets/Prefabs/A.prefab")
manage_asset(action="rename", path="Assets/A.prefab", destination="Assets/B.prefab")

# Create folder
manage_asset(action="create_folder", path="Assets/NewFolder")

# Delete
manage_asset(action="delete", path="Assets/OldAsset.asset")
```

### manage_prefabs

无界面（Headless）Prefab 操作。

```python
# Get prefab info
manage_prefabs(action="get_info", prefab_path="Assets/Prefabs/Player.prefab")

# Get prefab hierarchy
manage_prefabs(action="get_hierarchy", prefab_path="Assets/Prefabs/Player.prefab")

# Create prefab from scene GameObject
manage_prefabs(
    action="create_from_gameobject",
    target="Player",             # GameObject in scene
    prefab_path="Assets/Prefabs/Player.prefab",
    allow_overwrite=False
)

# Modify prefab contents (headless)
manage_prefabs(
    action="modify_contents",
    prefab_path="Assets/Prefabs/Player.prefab",
    target="ChildObject",        # object within prefab
    position=[0, 1, 0],
    components_to_add=["AudioSource"]
)
```

---

## 材质与 Shader 工具

### manage_material

创建并修改材质。

```python
# Create material
manage_material(
    action="create",
    material_path="Assets/Materials/Red.mat",
    shader="Standard",
    properties={"_Color": [1, 0, 0, 1]}
)

# Get material info
manage_material(action="get_material_info", material_path="Assets/Materials/Red.mat")

# Set shader property
manage_material(
    action="set_material_shader_property",
    material_path="Assets/Materials/Red.mat",
    property="_Metallic",
    value=0.8
)

# Set color
manage_material(
    action="set_material_color",
    material_path="Assets/Materials/Red.mat",
    property="_BaseColor",
    color=[0, 1, 0, 1]           # RGBA
)

# Assign to renderer
manage_material(
    action="assign_material_to_renderer",
    target="MyCube",
    material_path="Assets/Materials/Red.mat",
    slot=0                       # material slot index
)

# Set renderer color directly
manage_material(
    action="set_renderer_color",
    target="MyCube",
    color=[1, 0, 0, 1],
    mode="create_unique"          # Creates a unique .mat asset per object (persistent)
    # Other modes: "property_block" (default, not persistent),
    #              "shared" (mutates shared material — avoid for primitives),
    #              "instance" (runtime only, not persistent)
)
```

### manage_texture

创建程序化纹理。

```python
manage_texture(
    action="create",
    path="Assets/Textures/Checker.png",
    width=64,
    height=64,
    fill_color=[255, 255, 255, 255]  # or [1.0, 1.0, 1.0, 1.0]
)

# Apply pattern
manage_texture(
    action="apply_pattern",
    path="Assets/Textures/Checker.png",
    pattern="checkerboard",      # "checkerboard"|"stripes"|"dots"|"grid"|"brick"
    palette=[[0,0,0,255], [255,255,255,255]],
    pattern_size=8
)

# Apply gradient
manage_texture(
    action="apply_gradient",
    path="Assets/Textures/Gradient.png",
    gradient_type="linear",      # "linear"|"radial"
    gradient_angle=45,
    palette=[[255,0,0,255], [0,0,255,255]]
)
```

---

## UI 工具

### manage_ui

管理 Unity UI Toolkit 元素：UXML 文档、USS 样式表、UIDocument 组件及可视树检查。

```python
# Create a UXML file
manage_ui(
    action="create",
    path="Assets/UI/MainMenu.uxml",
    contents='<ui:UXML xmlns:ui="UnityEngine.UIElements"><ui:Label text="Hello" /></ui:UXML>'
)

# Create a USS stylesheet
manage_ui(
    action="create",
    path="Assets/UI/Styles.uss",
    contents=".title { font-size: 32px; color: white; }"
)

# Read a UXML/USS file
manage_ui(
    action="read",
    path="Assets/UI/MainMenu.uxml"
)
# Returns: {"success": true, "data": {"contents": "...", "path": "..."}}

# Update an existing file
manage_ui(
    action="update",
    path="Assets/UI/Styles.uss",
    contents=".title { font-size: 48px; color: yellow; -unity-font-style: bold; }"
)

# Attach UIDocument to a GameObject
manage_ui(
    action="attach_ui_document",
    target="UICanvas",                    # GameObject name or path
    source_asset="Assets/UI/MainMenu.uxml",
    panel_settings="Assets/UI/Panel.asset",  # optional, auto-creates if omitted
    sort_order=0                          # optional, default 0
)

# Create PanelSettings asset
manage_ui(
    action="create_panel_settings",
    path="Assets/UI/Panel.asset",
    scale_mode="ScaleWithScreenSize",     # optional: "ConstantPixelSize"|"ConstantPhysicalSize"|"ScaleWithScreenSize"
    reference_resolution={"width": 1920, "height": 1080}  # optional, for ScaleWithScreenSize
)

# Inspect the visual tree of a UIDocument
manage_ui(
    action="get_visual_tree",
    target="UICanvas",                    # GameObject with UIDocument
    max_depth=10                          # optional, default 10
)
# Returns: hierarchy of VisualElements with type, name, classes, styles, text, children
```

**UI Toolkit 工作流：**

1. 创建 UXML（结构，类似 HTML）与 USS（样式，类似 CSS）文件
2. 创建 PanelSettings 资源（或让 `attach_ui_document` 自动创建）
3. 创建空 GameObject，并挂载引用 UXML 的 UIDocument
4. 使用 `get_visual_tree` 检查结果

**重要：** 在 UXML 中必须使用 `<ui:Style>`（带 `ui:` 命名空间前缀），不要使用裸 `<Style>`。若无此前缀，UI Builder 可能无法打开该文件。

---

## 编辑器控制工具

### manage_editor

控制 Unity Editor 状态。

```python
manage_editor(action="play")               # Enter play mode
manage_editor(action="pause")              # Pause play mode
manage_editor(action="stop")               # Exit play mode

manage_editor(action="set_active_tool", tool_name="Move")  # Move/Rotate/Scale/etc.

manage_editor(action="add_tag", tag_name="Enemy")
manage_editor(action="remove_tag", tag_name="OldTag")

manage_editor(action="add_layer", layer_name="Projectiles")
manage_editor(action="remove_layer", layer_name="OldLayer")

manage_editor(action="close_prefab_stage")  # Exit prefab editing mode back to main scene

# Package deployment (no confirmation dialog — designed for LLM-driven iteration)
manage_editor(action="deploy_package")     # Copy configured MCPForUnity source into installed package
manage_editor(action="restore_package")    # Revert to pre-deployment backup
```

**部署流程：** 先在 MCP for Unity Advanced Settings 中设置源码路径。`deploy_package` 会把源码复制到项目包位置、创建备份并触发 `AssetDatabase.Refresh`。随后调用 `refresh_unity(wait_for_ready=True)` 以等待重新编译完成。

### execute_menu_item

执行任意 Unity 菜单项。

```python
execute_menu_item(menu_path="File/Save Project")
execute_menu_item(menu_path="GameObject/3D Object/Cube")
execute_menu_item(menu_path="Window/General/Console")
```

### read_console

读取或清空 Unity Console 消息。

```python
# Get recent messages
read_console(
    action="get",
    types=["error", "warning", "log"],  # or ["all"]
    count=10,                    # max messages (ignored with paging)
    filter_text="NullReference", # optional text filter
    page_size=50,
    cursor=0,
    format="detailed",           # "plain"|"detailed"|"json"
    include_stacktrace=True
)

# Clear console
read_console(action="clear")
```

---

## 测试工具

### run_tests

启动异步测试执行。

```python
result = run_tests(
    mode="EditMode",             # "EditMode"|"PlayMode"
    test_names=["MyTests.TestA", "MyTests.TestB"],  # specific tests
    group_names=["Integration*"],  # regex patterns
    category_names=["Unit"],     # NUnit categories
    assembly_names=["Tests"],    # assembly filter
    include_failed_tests=True,   # include failure details
    include_details=False        # include all test details
)
# Returns: {"job_id": "abc123", ...}
```

### get_test_job

轮询测试任务状态。

```python
result = get_test_job(
    job_id="abc123",
    wait_timeout=60,             # wait up to N seconds
    include_failed_tests=True,
    include_details=False
)
# Returns: {"status": "complete"|"running"|"failed", "results": {...}}
```

---

## 搜索工具

### find_in_file

使用正则表达式搜索文件内容。

```python
find_in_file(
    uri="mcpforunity://path/Assets/Scripts/MyScript.cs",
    pattern="public void \\w+",  # regex pattern
    max_results=200,
    ignore_case=True
)
# Returns: line numbers, content excerpts, match positions
```

---

## 自定义工具

### execute_custom_tool

执行项目自定义工具。

```python
execute_custom_tool(
    tool_name="my_custom_tool",
    parameters={"param1": "value", "param2": 42}
)
```

可通过 `mcpforunity://custom-tools` 资源发现可用的自定义工具。

---

## 相机工具

### manage_camera

统一相机管理（Unity Camera + Cinemachine）。未安装 Cinemachine 时可回退到基础 Camera；安装后可使用预设、管线与混合能力。可用 `ping` 检查可用性。

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|-----------|------|----------|-------------|
| `action` | string | 是 | 要执行的动作（见下方分类） |
| `target` | string | 有时 | 目标相机（名称、路径或实例 ID） |
| `search_method` | string | 否 | `by_id`、`by_name`、`by_path` |
| `properties` | dict \| string | 否 | 动作专用参数 |

**截图参数**（用于 `screenshot` 与 `screenshot_multiview`）：

| 参数 | 类型 | 说明 |
|-----------|------|-------------|
| `capture_source` | string | `"game_view"`（默认）或 `"scene_view"`（编辑器视口） |
| `view_target` | string\|int\|list | 聚焦目标（GO 名称/路径/ID 或 [x,y,z]）。game_view：用于相机朝向；scene_view：用于视口框选 |
| `camera` | string | 指定截图相机（默认 `Camera.main`），仅 game_view 生效 |
| `include_image` | bool | 以内联 base64 PNG 返回图像（默认 false） |
| `max_resolution` | int | 最大降采样分辨率（像素，默认 640） |
| `batch` | string | `"surround"`（6 角度）或 `"orbit"`（可配置网格），仅 game_view 生效 |
| `view_position` | list[float] | 放置相机的世界坐标 [x,y,z]，仅 game_view 生效 |
| `view_rotation` | list[float] | 欧拉旋转 [x,y,z]（会覆盖 `view_target`），仅 game_view 生效 |

**按类别划分的动作：**

**基础设置：**
- `ping` — 检查 Cinemachine 是否可用及其版本
- `ensure_brain` — 确保主相机上存在 CinemachineBrain。属性：`camera`（目标相机）、`defaultBlendStyle`、`defaultBlendDuration`
- `get_brain_status` — 获取 Brain 状态（当前激活相机、混合状态）

**创建：**
- `create_camera` — 创建相机并可选预设。属性：`name`、`preset`（follow/third_person/freelook/dolly/static/top_down/side_scroller）、`follow`、`lookAt`、`priority`、`fieldOfView`。未安装 Cinemachine 时回退到基础 Camera。

**配置：**
- `set_target` — 设置 Follow 和/或 LookAt 目标。属性：`follow`、`lookAt`（GO 名称/路径/ID）
- `set_priority` — 设置相机优先级供 Brain 选择。属性：`priority`（int）
- `set_lens` — 配置镜头参数。属性：`fieldOfView`、`nearClipPlane`、`farClipPlane`、`orthographicSize`、`dutch`
- `set_body` — 配置 Body 组件（Cinemachine）。属性：`bodyType`（用于切换）及对应组件专属参数
- `set_aim` — 配置 Aim 组件（Cinemachine）。属性：`aimType`（用于切换）及对应组件专属参数
- `set_noise` — 配置噪声（Cinemachine）。属性：`amplitudeGain`、`frequencyGain`

**扩展（Cinemachine）：**
- `add_extension` — 添加扩展。属性：`extensionType`（如 CinemachineConfiner2D、CinemachineDeoccluder、CinemachineImpulseListener、CinemachineFollowZoom、CinemachineRecomposer 等）
- `remove_extension` — 按类型移除扩展。属性：`extensionType`

**控制：**
- `list_cameras` — 列出所有相机及其状态
- `set_blend` — 配置 Brain 的默认混合。属性：`style`（Cut/EaseInOut/Linear 等）、`duration`
- `force_camera` — 强制 Brain 使用指定相机
- `release_override` — 释放相机强制覆盖

**捕获：**
- `screenshot` — 截图。支持 `capture_source="game_view"`（默认，基于相机）或 `"scene_view"`（编辑器视口）。game_view 支持内联 base64、surround/orbit 批量截图与定位截图；scene_view 支持 `view_target` 框选。
- `screenshot_multiview` — `screenshot` 的快捷形式（`batch='surround'` 且 `include_image=true`）。

**示例：**

```python
# Check Cinemachine availability
manage_camera(action="ping")

# Create a third-person camera following the player
manage_camera(action="create_camera", properties={
    "name": "FollowCam", "preset": "third_person",
    "follow": "Player", "lookAt": "Player", "priority": 20
})

# Ensure Brain exists on main camera
manage_camera(action="ensure_brain")

# Configure body component
manage_camera(action="set_body", target="FollowCam", properties={
    "bodyType": "CinemachineThirdPersonFollow",
    "cameraDistance": 5.0, "shoulderOffset": [0.5, 0.5, 0]
})

# Set aim
manage_camera(action="set_aim", target="FollowCam", properties={
    "aimType": "CinemachineRotationComposer"
})

# Add camera shake
manage_camera(action="set_noise", target="FollowCam", properties={
    "amplitudeGain": 0.5, "frequencyGain": 1.0
})

# Set priority to make this the active camera
manage_camera(action="set_priority", target="FollowCam", properties={"priority": 50})

# Force a specific camera
manage_camera(action="force_camera", target="CinematicCam")

# Release override (return to priority-based selection)
manage_camera(action="release_override")

# Configure blend transitions
manage_camera(action="set_blend", properties={"style": "EaseInOut", "duration": 2.0})

# Add deoccluder extension
manage_camera(action="add_extension", target="FollowCam", properties={
    "extensionType": "CinemachineDeoccluder"
})

# Screenshot from a specific camera (game_view, default)
manage_camera(action="screenshot", camera="FollowCam", include_image=True, max_resolution=512)

# Scene View screenshot (captures editor viewport — gizmos, wireframes, grid)
manage_camera(action="screenshot", capture_source="scene_view", include_image=True)

# Scene View screenshot framed on a specific object
manage_camera(action="screenshot", capture_source="scene_view", view_target="Canvas", include_image=True)

# Multi-view screenshot (6-angle contact sheet)
manage_camera(action="screenshot_multiview", max_resolution=480)

# List all cameras
manage_camera(action="list_cameras")
```

**分层机制：**
- Tier 1 动作（ping、create_camera、set_target、set_lens、set_priority、list_cameras、screenshot、screenshot_multiview）在没有 Cinemachine 时也可使用——会自动回退到基础 Unity Camera。
- Tier 2 动作（ensure_brain、get_brain_status、set_body、set_aim、set_noise、add/remove_extension、set_blend、force_camera、release_override）依赖 `com.unity.cinemachine`。若未安装则会返回错误并给出回退建议。

**资源：** 修改前建议读取 `mcpforunity://scene/cameras` 获取当前相机状态。

---

## 图形工具

### manage_graphics

统一渲染与图形管理：Volume/后处理、光照烘焙、渲染统计、管线配置以及 URP 渲染器特性。涉及 Volume/Feature 的动作需要 URP 或 HDRP。可用 `ping` 检查管线状态和可用特性。

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|-----------|------|----------|-------------|
| `action` | string | 是 | 要执行的动作（见下方分类） |
| `target` | string | 有时 | 目标对象名称或实例 ID |
| `effect` | string | 有时 | 效果类型名（如 `Bloom`、`Vignette`） |
| `properties` | dict | 否 | 需要设置的动作专用属性 |
| `parameters` | dict | 否 | 效果参数值 |
| `settings` | dict | 否 | 烘焙或管线设置 |
| `name` | string | 否 | 创建对象时使用的名称 |
| `profile_path` | string | 否 | VolumeProfile 的资源路径 |
| `path` | string | 否 | 资源路径（用于 `volume_create_profile`） |
| `position` | list[float] | 否 | 位置 [x,y,z] |

**按类别划分的动作：**

**状态：**
- `ping` — 检查渲染管线类型、可用特性与包状态

**Volume（需要 URP/HDRP）：**
- `volume_create` — 创建 Volume GameObject，并可选附带效果。属性：`name`、`is_global`（默认 true）、`weight`（0-1）、`priority`、`profile_path`（已有 profile）、`effects`（效果定义列表）
- `volume_add_effect` — 向 Volume 添加效果覆盖。参数：`target`（Volume GO）、`effect`（如 `"Bloom"`）
- `volume_set_effect` — 设置效果参数。参数：`target`、`effect`、`parameters`（参数名到值的 dict）
- `volume_remove_effect` — 移除效果覆盖。参数：`target`、`effect`
- `volume_get_info` — 获取 Volume 详情（profile、效果、参数）。参数：`target`
- `volume_set_properties` — 设置 Volume 组件属性（weight、priority、isGlobal）。参数：`target`、`properties`
- `volume_list_effects` — 列出当前管线可用的全部 volume 效果
- `volume_create_profile` — 创建独立 VolumeProfile 资源。参数：`path`、`effects`（可选）

**烘焙（仅 Edit 模式）：**
- `bake_start` — 开始光照贴图烘焙。参数：`async_bake`（默认 true）
- `bake_cancel` — 取消进行中的烘焙
- `bake_status` — 检查烘焙进度
- `bake_clear` — 清除已烘焙光照贴图数据
- `bake_reflection_probe` — 烘焙指定反射探针。参数：`target`
- `bake_get_settings` — 获取当前 Lightmapping 设置
- `bake_set_settings` — 设置 Lightmapping 参数。参数：`settings`（dict）
- `bake_create_light_probe_group` — 创建 Light Probe Group。参数：`name`、`position`、`grid_size` [x,y,z]、`spacing`
- `bake_create_reflection_probe` — 创建 Reflection Probe。参数：`name`、`position`、`size` [x,y,z]、`resolution`、`mode`、`hdr`、`box_projection`
- `bake_set_probe_positions` — 手动设置 Light Probe 位置。参数：`target`、`positions`（[x,y,z] 数组）

**统计：**
- `stats_get` — 获取渲染计数器（draw calls、batches、triangles、vertices 等）
- `stats_list_counters` — 列出全部可用 ProfilerRecorder 计数器
- `stats_set_scene_debug` — 设置 Scene View 调试/绘制模式。参数：`mode`
- `stats_get_memory` — 获取渲染内存占用

**管线：**
- `pipeline_get_info` — 获取当前渲染管线信息（类型、质量等级、资源路径）
- `pipeline_set_quality` — 切换质量等级。参数：`level`（名称或索引）
- `pipeline_get_settings` — 获取管线资源设置
- `pipeline_set_settings` — 设置管线资源参数。参数：`settings`（dict）

**特性（仅 URP）：**
- `feature_list` — 列出当前 URP 渲染器上的 renderer features
- `feature_add` — 添加 renderer feature。参数：`feature_type`、`name`、`material`（用于全屏效果）
- `feature_remove` — 移除 renderer feature。参数：`index` 或 `name`
- `feature_configure` — 设置 feature 属性。参数：`index` 或 `name`、`properties`（dict）
- `feature_toggle` — 启用/禁用 feature。参数：`index` 或 `name`、`active`（bool）
- `feature_reorder` — 调整 feature 顺序。参数：`order`（索引列表）

**示例：**

```python
# Check pipeline status
manage_graphics(action="ping")

# Create a global post-processing volume with Bloom and Vignette
manage_graphics(action="volume_create", name="PostProcessing", is_global=True,
    effects=[
        {"type": "Bloom", "parameters": {"intensity": 1.5, "threshold": 0.9}},
        {"type": "Vignette", "parameters": {"intensity": 0.4}}
    ])

# Add an effect to an existing volume
manage_graphics(action="volume_add_effect", target="PostProcessing", effect="ColorAdjustments")

# Configure effect parameters
manage_graphics(action="volume_set_effect", target="PostProcessing",
    effect="ColorAdjustments", parameters={"postExposure": 0.5, "saturation": 10})

# Get volume info
manage_graphics(action="volume_get_info", target="PostProcessing")

# List all available effects for the active pipeline
manage_graphics(action="volume_list_effects")

# Create a VolumeProfile asset
manage_graphics(action="volume_create_profile", path="Assets/Settings/MyProfile.asset",
    effects=[{"type": "Bloom"}, {"type": "Tonemapping"}])

# Start async lightmap bake
manage_graphics(action="bake_start", async_bake=True)

# Check bake progress
manage_graphics(action="bake_status")

# Create a Light Probe Group with a 3x2x3 grid
manage_graphics(action="bake_create_light_probe_group", name="ProbeGrid",
    position=[0, 1, 0], grid_size=[3, 2, 3], spacing=2.0)

# Create a Reflection Probe
manage_graphics(action="bake_create_reflection_probe", name="RoomProbe",
    position=[0, 2, 0], size=[10, 5, 10], resolution=256, hdr=True)

# Get rendering stats
manage_graphics(action="stats_get")

# Get memory usage
manage_graphics(action="stats_get_memory")

# Get pipeline info
manage_graphics(action="pipeline_get_info")

# Switch quality level
manage_graphics(action="pipeline_set_quality", level="High")

# List URP renderer features
manage_graphics(action="feature_list")

# Add a full-screen renderer feature
manage_graphics(action="feature_add", feature_type="FullScreenPassRendererFeature",
    name="NightVision", material="Assets/Materials/NightVision.mat")

# Toggle a feature off
manage_graphics(action="feature_toggle", index=0, active=False)

# Reorder features
manage_graphics(action="feature_reorder", order=[2, 0, 1])
```

**资源：**
- `mcpforunity://scene/volumes` — 列出场景中所有 Volume 组件及其 profile/效果
- `mcpforunity://rendering/stats` — 当前渲染性能计数器
- `mcpforunity://pipeline/renderer-features` — 当前激活渲染器上的 URP renderer features

---

## 包管理工具

### manage_packages

管理 Unity 包：查询、安装、移除、嵌入与 registry 配置。安装/移除会触发域重载。

**查询动作（只读）：**

| 动作 | 参数 | 说明 |
|--------|-----------|-------------|
| `list_packages` | — | 列出已安装包（异步，返回 job_id） |
| `search_packages` | `query` | 按关键字搜索 Unity registry（异步，返回 job_id） |
| `get_package_info` | `package` | 获取指定已安装包的详细信息 |
| `list_registries` | — | 列出所有 scoped registry（名称、URL、scope）；立即返回 |
| `ping` | — | 检查包管理器可用性、Unity 版本、包数量 |
| `status` | `job_id` (required for list/search; optional for add/remove/embed) | 轮询异步任务状态；省略 job_id 时轮询最新 add/remove/embed 任务 |

**修改类动作：**

| 动作 | 参数 | 说明 |
|--------|-----------|-------------|
| `add_package` | `package` | 安装包（支持 name、name@version、git URL 或 file: path） |
| `remove_package` | `package`, `force` (optional) | 移除包；若存在依赖方则会阻止，除非 `force=true` |
| `embed_package` | `package` | 将包复制到本地 `Packages/` 目录以便编辑 |
| `resolve_packages` | — | 强制重新解析全部包 |
| `add_registry` | `name`, `url`, `scopes` | 添加 scoped registry（如 OpenUPM） |
| `remove_registry` | `name` or `url` | 移除 scoped registry |

**输入校验：**
- 合法包 ID 示例：`com.unity.inputsystem`、`com.unity.cinemachine@3.1.6`
- Git URL：允许，但会给出警告（“请确认来源可信”）
- `file:` 路径：允许，但会给出警告
- 非法名称（含大写、缺少点分结构）：会被拒绝

**示例 — 列出已安装包：**
```python
manage_packages(action="list_packages")
# Returns job_id, then poll:
manage_packages(action="status", job_id="<job_id>")
```

**示例 — 搜索包：**
```python
manage_packages(action="search_packages", query="input system")
```

**示例 — 安装包：**
```python
manage_packages(action="add_package", package="com.unity.inputsystem")
# Poll until complete:
manage_packages(action="status", job_id="<job_id>")
```

**示例 — 带依赖检查的移除：**
```python
manage_packages(action="remove_package", package="com.unity.modules.ui")
# Error: "Cannot remove: 3 package(s) depend on it: ..."
manage_packages(action="remove_package", package="com.unity.modules.ui", force=True)
# Proceeds anyway
```

**示例 — 添加 OpenUPM registry：**
```python
manage_packages(
    action="add_registry",
    name="OpenUPM",
    url="https://package.openupm.com",
    scopes=["com.cysharp", "com.neuecc"]
)
```

---

## ProBuilder 工具

### manage_probuilder

统一的 ProBuilder 网格操作工具。依赖 `com.unity.probuilder` 包。可用时，对于可编辑几何体、多材质面或复杂形体，**优先使用 ProBuilder 而不是 primitive GameObject**。

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|-----------|------|----------|-------------|
| `action` | string | Yes | 要执行的动作（见下方分类） |
| `target` | string | Sometimes | 目标 GameObject 名称/路径/ID |
| `search_method` | string | No | 查找目标的方法：`by_id`、`by_name`、`by_path`、`by_tag`、`by_layer` |
| `properties` | dict \| string | No | 动作专用参数（dict 或 JSON 字符串） |

**按类别划分的动作：**

**形状创建：**
- `create_shape` — 创建 ProBuilder 基础形体（shape_type、size、position、rotation、name）。支持 12 种：Cube、Cylinder、Sphere、Plane、Cone、Torus、Pipe、Arch、Stair、CurvedStair、Door、Prism
- `create_poly_shape` — 基于二维多边形轮廓创建（points、extrudeHeight、flipNormals）

**网格编辑：**
- `extrude_faces` — 挤出面（faceIndices、distance、method: FaceNormal/VertexNormal/IndividualFaces）
- `extrude_edges` — 挤出边（edgeIndices 或 edges [{a,b},...]、distance、asGroup）
- `bevel_edges` — 倒角边（edgeIndices 或 edges [{a,b},...]、amount 0-1）
- `subdivide` — 使用 ConnectElements 细分面（faceIndices 可选）
- `delete_faces` — 删除面（faceIndices）
- `bridge_edges` — 桥接两条开口边（edgeA、edgeB 以 {a,b} 表示，allowNonManifold）
- `connect_elements` — 连接边/面（edgeIndices 或 faceIndices）
- `detach_faces` — 将面分离为新对象（faceIndices、deleteSourceFaces）
- `flip_normals` — 翻转法线（faceIndices）
- `merge_faces` — 合并多个面为一个（faceIndices）
- `combine_meshes` — 合并多个 ProBuilder 对象（targets 列表）
- `merge_objects` — 合并对象并自动转换（targets、name）
- `duplicate_and_flip` — 创建双面几何体（faceIndices）
- `create_polygon` — 将已有顶点连接成新面（vertexIndices，顺序可无序）

**顶点操作：**
- `merge_vertices` — 将多个顶点塌陷为一个点（vertexIndices、collapseToFirst）
- `weld_vertices` — 按邻近半径焊接顶点（vertexIndices、radius）
- `split_vertices` — 拆分共享顶点（vertexIndices）
- `move_vertices` — 平移顶点（vertexIndices、offset [x,y,z]）
- `insert_vertex` — 在边或面上插入顶点（edge {a,b} 或 faceIndex + point [x,y,z]）
- `append_vertices_to_edge` — 在边上插入等距点（edgeIndices 或 edges、count）

**选择：**
- `select_faces` — 按条件选择面（direction + tolerance，growFrom + growAngle）

**UV 与材质：**
- `set_face_material` — 为面指定材质（faceIndices、materialPath）
- `set_face_color` — 为面设置顶点色（faceIndices、color [r,g,b,a]）
- `set_face_uvs` — 设置 UV 参数（faceIndices、scale、offset、rotation、flipU、flipV）

**查询：**
- `get_mesh_info` — 使用 `include` 参数获取网格详情：
  - `"summary"`（默认）：计数、包围盒、材质
  - `"faces"`：额外返回面法线、中心点与方向标签（最多 100 条）
  - `"edges"`：额外返回边顶点对及其世界坐标（最多 200 条，已去重）
  - `"all"`：返回全部信息
- `ping` — 检查 ProBuilder 是否可用

**平滑：**
- `set_smoothing` — 为面设置平滑组（faceIndices、smoothingGroup：0=硬边，1+=平滑）
- `auto_smooth` — 按角度自动分配平滑组（angleThreshold，默认 30）

**网格工具：**
- `center_pivot` — 将 pivot 移动到网格包围盒中心
- `freeze_transform` — 将 Transform 烘焙进顶点并重置 Transform
- `validate_mesh` — 检查网格健康状态（只读诊断）
- `repair_mesh` — 自动修复退化三角形

**暂不可用（已知问题）：**
- `set_pivot` — 顶点位置在网格重建后不会持久化。请改用 `center_pivot` 或直接使用 Transform 定位。
- `convert_to_probuilder` — `MeshImporter` 内部会抛错。建议改为原生创建形体。

**示例：**

```python
# Check availability
manage_probuilder(action="ping")

# Create a cube
manage_probuilder(action="create_shape", properties={"shape_type": "Cube", "name": "MyCube"})

# Get face info with directions
manage_probuilder(action="get_mesh_info", target="MyCube", properties={"include": "faces"})

# Extrude the top face (find it via direction="top" in get_mesh_info results)
manage_probuilder(action="extrude_faces", target="MyCube",
    properties={"faceIndices": [2], "distance": 1.5})

# Select all upward-facing faces
manage_probuilder(action="select_faces", target="MyCube",
    properties={"direction": "up", "tolerance": 0.7})

# Create double-sided geometry (for room interiors)
manage_probuilder(action="duplicate_and_flip", target="Room",
    properties={"faceIndices": [0, 1, 2, 3, 4, 5]})

# Weld nearby vertices
manage_probuilder(action="weld_vertices", target="MyCube",
    properties={"vertexIndices": [0, 1, 2, 3], "radius": 0.1})

# Auto-smooth
manage_probuilder(action="auto_smooth", target="MyCube", properties={"angleThreshold": 30})

# Cleanup workflow
manage_probuilder(action="center_pivot", target="MyCube")
manage_probuilder(action="validate_mesh", target="MyCube")
```

另见：[ProBuilder Workflow Guide](probuilder-guide.md)，其中包含更详细的模式和复杂对象示例。

---

## 文档工具

用于校验 Unity C# API 并获取官方文档的工具。分组：`docs`。

### `unity_reflect`

通过反射检查 Unity 运行时 C# API。**在编写引用 Unity API 的 C# 代码前，务必先使用此工具**——LLM 训练数据中经常存在错误、过期或幻觉 API。

需要已连接 Unity。

| 参数 | 类型 | 必填 | 说明 |
|-----------|------|----------|-------------|
| `action` | string | Yes | `search`、`get_type` 或 `get_member` |
| `class_name` | string | For get_type, get_member | 完整限定名或简写 C# 类名 |
| `member_name` | string | For get_member | 要检查的方法、属性或字段名 |
| `query` | string | For search | 类型名搜索查询 |
| `scope` | string | No | 搜索的程序集范围：`unity`、`packages`、`project`、`all`（默认：`unity`） |

**动作：**

- **`search`**：在已加载程序集里按名称搜索类型。返回匹配的类型名。
- **`get_type`**：获取某个类的成员摘要（仅名称）。返回方法、属性、字段列表。
- **`get_member`**：获取单个成员的完整签名细节。返回参数类型、返回类型和重载信息。

```python
# Search for types matching a name
unity_reflect(action="search", query="NavMesh")
unity_reflect(action="search", query="Camera", scope="all")

# Get all members of a type
unity_reflect(action="get_type", class_name="UnityEngine.AI.NavMeshAgent")

# Get detailed signature for a specific member
unity_reflect(action="get_member", class_name="Physics", member_name="Raycast")
unity_reflect(action="get_member", class_name="NavMeshAgent", member_name="SetDestination")
```

### `unity_docs`

从 docs.unity3d.com 拉取 Unity 官方文档。返回描述、参数细节、代码示例与注意事项。建议在 `unity_reflect` 确认类型存在后使用。

获取文档本身不需要 Unity 连接。若 `lookup` 查询与资源相关（asset-related），还会同时搜索项目资源（该部分需要 Unity 连接）。

| 参数 | 类型 | 必填 | 说明 |
|-----------|------|----------|-------------|
| `action` | string | Yes | `get_doc`、`get_manual`、`get_package_doc` 或 `lookup` |
| `class_name` | string | For get_doc | Unity 类名（如 `Physics`、`Transform`） |
| `member_name` | string | No | `get_doc` 时可选的方法或属性名 |
| `version` | string | No | Unity 版本（如 `6000.0.38f1`）。会自动提取 major.minor |
| `slug` | string | For get_manual | Manual 页面 slug（如 `execution-order`） |
| `package` | string | For get_package_doc, optional for lookup | 包名（如 `com.unity.render-pipelines.universal`） |
| `page` | string | For get_package_doc | 包文档页面（如 `index`、`2d-index`） |
| `pkg_version` | string | For get_package_doc, optional for lookup | 包版本 major.minor（如 `17.0`） |
| `query` | string | For lookup (single) | 单条搜索查询 |
| `queries` | string | For lookup (batch) | 逗号分隔的批量查询（如 `Physics.Raycast,NavMeshAgent,Light2D`） |

**动作：**

- **`get_doc`**：获取类或成员的 ScriptReference 文档。会解析 HTML 提取描述、签名、参数、返回类型及代码示例。
- **`get_manual`**：按 slug 获取 Unity Manual 页面。返回标题、章节与代码示例。
- **`get_package_doc`**：获取包文档。需要提供包名、页面 slug 与包版本。
- **`lookup`**：并行搜索文档来源（ScriptReference + Manual；若提供 `package` + `pkg_version` 也会检索包文档）。支持批量查询。对于与资源相关的查询（shader、material、texture 等），还会通过 `manage_asset` 搜索项目资源。

```python
# Fetch ScriptReference for a class
unity_docs(action="get_doc", class_name="Physics")
unity_docs(action="get_doc", class_name="Physics", member_name="Raycast")
unity_docs(action="get_doc", class_name="Transform", version="6000.0.38f1")

# Fetch a Manual page
unity_docs(action="get_manual", slug="execution-order")
unity_docs(action="get_manual", slug="urp/urp-introduction")

# Fetch package documentation
unity_docs(action="get_package_doc", package="com.unity.render-pipelines.universal",
           page="2d-index", pkg_version="17.0")

# Parallel lookup across all sources (single query)
unity_docs(action="lookup", query="Physics.Raycast")

# Batch lookup (multiple queries in one call)
unity_docs(action="lookup", queries="Physics.Raycast,NavMeshAgent,Light2D")

# Lookup with package docs included
unity_docs(action="lookup", query="VolumeProfile",
           package="com.unity.render-pipelines.universal", pkg_version="17.0")
```
