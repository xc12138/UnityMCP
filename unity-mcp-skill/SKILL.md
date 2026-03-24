---
name: unity-mcp-orchestrator
description: 通过 MCP（Model Context Protocol）工具和资源编排 Unity Editor。适用于通过 MCP for Unity 操作 Unity 项目时：创建/修改 GameObject、编辑脚本、管理场景、运行测试，或任何 Unity 编辑器自动化场景。提供最佳实践、工具参数规范和工作流模式，帮助你高效集成 Unity-MCP。
---

# Unity-MCP 操作指南

这个 skill 帮助你更有效地使用 MCP 工具与资源操作 Unity Editor。

## 模板说明

`references/workflows.md` 和 `references/tools-reference.md` 中的示例是可复用模板。它们在不同 Unity 版本、包配置（UGUI/TMP/Input System）以及项目约定下可能并不完全准确。实现后请务必检查控制台、编译错误，或使用截图进行验证。

默认策略：
- 只读取当前任务真正需要的资源，不做全量预检。
- 只做一种验证：编译类看控制台，视觉类看截图，结构类回读资源。
- 工具失败、目标不明确或项目状态异常时，再升级到完整排障流程。

## 最小默认流程

大多数任务按这 4 步执行即可：

```text
1. 最小发现   → 读取一个必要资源，或直接定位目标对象
2. 执行变更   → 优先用高层工具；可批量时用 batch_execute
3. 单通道验证 → 脚本/包改动查 console；视觉改动截图；结构改动回读资源
4. 失败再升级 → busy / 编译中 / 域重载 / 多实例 / stale_file 时再补检查
```

不要默认执行这些动作，除非任务确实需要：
- 读取 `mcpforunity://scene/gameobject-api`
- 全场景 `find_gameobjects`
- 截图验证
- `validate_script`
- `get_sha`
- 检查 `mcpforunity://instances`

## 什么时候先读资源

优先只读一个最小资源：
- 脚本、编译、连接异常：`mcpforunity://editor/state`
- UI、输入系统、渲染管线：`mcpforunity://project/info`
- 目标对象不明确：`find_gameobjects` 或对应对象资源
- 需要确认结构：读取对应 scene / asset / component 资源

不需要为了“保险”先读所有资源。

## 什么时候必须升级检查

遇到以下情况，再进入重型流程：
- 工具返回 `busy`
- `is_compiling` 或 `is_domain_reload_pending` 为 `true`
- 命令无声失败
- 场景里有多个同名对象，目标不明确
- 同时存在多个 Unity Editor 实例
- 出现 `stale_file`

最常见升级动作：
- 读 `mcpforunity://editor/state`
- 读 `mcpforunity://instances`
- `find_gameobjects`
- `get_sha`
- 详细 `read_console`

## 高风险操作

以下操作不要默认自动执行，除非用户明确要求，或你已确认风险可接受：
- `manage_scene(action="create")` 替换当前场景
- 删除脚本、资源或对象
- 包源、registry、Git URL 相关安装
- 大规模批量修改现有层级

这类操作优先先确认目标、范围和是否覆盖现有内容。

## 防循环护栏

出现问题时，不要无限重试。必须遵守以下停止规则：

- 同一种失败最多重试 2 次。
- 如果错误信息、编辑器状态和目标文件都没有变化，不要继续同一路径重试。
- `editor/state` 轮询最多 3 次；若状态持续不变，则停止自动处理并转人工确认。
- 连续 2 次出现相同或等价的 console 错误时，停止自动修复。
- 单轮排障只允许一种高成本验证：截图、全量资源读取、批量搜索三者选一，不要叠加。
- 如果无法明确定位根因，不要靠继续试错来换取信息，直接请求人工决策。

只有出现新的证据时，才允许继续下一轮：
- console 错误内容发生变化
- `editor_state` 状态发生变化
- 文件内容或 SHA 发生变化
- 截图或资源回读显示了新现象

以下情况优先停止自动循环并转人工：
- 多实例冲突
- 同名对象无法唯一定位
- 包安装、域重载或编译长时间卡住
- 编译错误扩散到多个脚本或多个系统
- 需要覆盖或删除用户现有内容

## 高频规则

### 脚本创建或编辑后

`create_script` 和 `script_apply_edits` 会自动触发导入与编译。不要额外调用刷新类动作。

```python
# 写入脚本
create_script(...)  # 或 script_apply_edits(...)

# 等待编译完成
# 读取 mcpforunity://editor/state → 等待 is_compiling == false

# 只检查错误
read_console(types=["error"], count=10)
```

默认不加：
- `validate_script`
- `get_sha`

仅在高风险重写、并发修改或文本锚点不稳定时再加。

### 多个独立操作

能批量就批量，减少往返调用：

```python
batch_execute(
    commands=[
        {"tool": "manage_gameobject", "params": {"action": "create", "name": "Cube1", "primitive_type": "Cube"}},
        {"tool": "manage_gameobject", "params": {"action": "create", "name": "Cube2", "primitive_type": "Cube"}}
    ],
    parallel=True
)
```

若命令有依赖关系，用 `fail_fast=True`。默认每批尽量保持小而清晰。

### 视觉改动后

只在用户关心画面、布局、相机、UI 或渲染结果时截图：

```python
manage_camera(action="screenshot", include_image=True, max_resolution=512)
```

不要把截图当成所有任务的默认收尾步骤。

### UI 任务

先读 `mcpforunity://project/info` 判断：
- `packages.uiToolkit` 为 `true` 时，优先 `manage_ui`
- `packages.ugui` 为 `true` 时，可用 Canvas + `manage_components`
- 文本优先 TMP 能力

主流程只需要先判断 UI 路线；Canvas、EventSystem、RectTransform 等细节去看参考工作流，不必全部搬进默认步骤。

### API 与文档校验

不确定 API 名称、签名或版本兼容性时，再使用：
- `unity_reflect`
- `unity_docs`

可信度优先级：
- reflection
- project assets
- docs

## 常用最小工作流

### 新建脚本并挂载

```python
create_script(
    path="Assets/Scripts/PlayerController.cs",
    contents="using UnityEngine;\n\npublic class PlayerController : MonoBehaviour\n{\n    void Update() { }\n}"
)

# 读取 mcpforunity://editor/state → 等待 is_compiling == false
read_console(types=["error"], count=10)
manage_gameobject(action="modify", target="Player", components_to_add=["PlayerController"])
```

### 查找并修改对象

```python
result = find_gameobjects(search_term="Enemy", search_method="by_tag", page_size=20)
# 必要时再回读对象资源
manage_gameobject(action="modify", target=result["ids"][0], position=[10, 0, 0])
```

### 运行测试

```python
result = run_tests(mode="EditMode", test_names=["MyTests.TestSomething"])
job_id = result["job_id"]
get_test_job(job_id=job_id, wait_timeout=60, include_failed_tests=True)
```

## 参数约定

常见值通常接受以下形式，但具体仍以当前工具 schema 和运行时返回为准。

```python
position=[1.0, 2.0, 3.0]
include_inactive=True
color=[1.0, 0.0, 0.0, 1.0]
path="Assets/Scripts/MyScript.cs"
uri="mcpforunity://path/Assets/Scripts/MyScript.cs"
```

`manage_components.set_property` 的 payload 经常因组件不同而变化；模板失败时，先看当前资源返回的真实结构。

## 错误恢复

| 现象 | 优先动作 |
|------|----------|
| 工具返回 `busy` | 读取 `editor/state`，等待编译或域重载结束 |
| `stale_file` | 重新 `get_sha` 后重试 |
| 连接丢失 | 等待几秒后重连，再读 `editor/state` |
| 命令无声失败 | 检查是否多实例，必要时 `set_active_instance` |

## 参考文件

需要更多细节时再读：
- [tools-reference.md](references/tools-reference.md)：完整工具文档与参数
- [resources-reference.md](references/resources-reference.md)：所有可用资源及数据格式
- [workflows.md](references/workflows.md)：扩展工作流、UI 细节和排障模式
