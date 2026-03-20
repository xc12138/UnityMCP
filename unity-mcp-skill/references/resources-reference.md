# Unity-MCP 资源参考

资源提供对 Unity 状态的只读访问。建议先用资源检查状态，再使用工具进行修改。

## 目录

- [编辑器状态资源](#editor-state-resources)
- [相机资源](#camera-resources)
- [图形资源](#graphics-resources)
- [场景与 GameObject 资源](#scene--gameobject-resources)
- [Prefab 资源](#prefab-resources)
- [项目资源](#project-resources)
- [实例资源](#instance-resources)
- [测试资源](#test-resources)

---

## URI 规范

所有资源都使用 `mcpforunity://` 前缀：

```
mcpforunity://{category}/{resource_path}[?query_params]
```

**分类：** `editor`, `scene`, `prefab`, `project`, `pipeline`, `rendering`, `menu-items`, `custom-tools`, `tests`, `instances`

---

## 编辑器状态资源

### mcpforunity://editor/state

**用途：** 编辑器就绪状态快照——在执行工具操作前检查。

**返回：**
```json
{
  "unity_version": "6000.3.2f1",
  "is_compiling": false,
  "is_domain_reload_pending": false,
  "play_mode": {
    "is_playing": false,
    "is_paused": false
  },
  "active_scene": {
    "path": "Assets/Scenes/Main.unity",
    "name": "Main"
  },
  "ready_for_tools": true,
  "blocking_reasons": [],
  "recommended_retry_after_ms": null,
  "staleness": {
    "age_ms": 150,
    "is_stale": false
  }
}
```

**关键字段：**
- `ready_for_tools`：仅当为 `true` 时再继续
- `is_compiling`：若为 `true` 需等待
- `blocking_reasons`：说明工具可能失败原因的数组
- `recommended_retry_after_ms`：建议等待时长

### mcpforunity://editor/selection

**用途：** 当前选中的对象。

**返回：**
```json
{
  "activeObject": "Player",
  "activeGameObject": "Player",
  "activeInstanceID": 12345,
  "count": 3,
  "gameObjects": ["Player", "Enemy", "Wall"],
  "assetGUIDs": []
}
```

### mcpforunity://editor/active-tool

**用途：** 当前编辑器工具状态。

**返回：**
```json
{
  "activeTool": "Move",
  "isCustom": false,
  "pivotMode": "Center",
  "pivotRotation": "Global"
}
```

### mcpforunity://editor/windows

**用途：** 所有已打开的编辑器窗口。

**返回：**
```json
{
  "windows": [
    {
      "title": "Scene",
      "typeName": "UnityEditor.SceneView",
      "isFocused": true,
      "position": {"x": 0, "y": 0, "width": 800, "height": 600}
    }
  ]
}
```

### mcpforunity://editor/prefab-stage

**用途：** 当前 Prefab 编辑上下文。

**返回：**
```json
{
  "isOpen": true,
  "assetPath": "Assets/Prefabs/Player.prefab",
  "prefabRootName": "Player",
  "isDirty": false
}
```

---

## 相机资源

### mcpforunity://scene/cameras

**用途：** 列出场景中全部相机（Unity Camera + CinemachineCamera）及完整状态。在使用 `manage_camera` 前建议先读取，以了解当前相机配置。

**返回：**
```json
{
  "brain": {
    "exists": true,
    "gameObject": "Main Camera",
    "instanceID": 55504,
    "activeCameraName": "Cam_Cinematic",
    "activeCameraID": -39420,
    "isBlending": false
  },
  "cinemachineCameras": [
    {
      "instanceID": -39420,
      "name": "Cam_Cinematic",
      "isLive": true,
      "priority": 50,
      "follow": {"name": "CameraTarget", "instanceID": -26766},
      "lookAt": {"name": "CameraTarget", "instanceID": -26766},
      "body": "CinemachineThirdPersonFollow",
      "aim": "CinemachineRotationComposer",
      "noise": "CinemachineBasicMultiChannelPerlin",
      "extensions": []
    }
  ],
  "unityCameras": [
    {
      "instanceID": 55504,
      "name": "Main Camera",
      "depth": 0.0,
      "fieldOfView": 50.0,
      "hasBrain": true
    }
  ],
  "cinemachineInstalled": true
}
```

**关键字段：**
- `brain`：CinemachineBrain 状态——当前激活相机、混合状态
- `cinemachineCameras`：所有 CinemachineCamera 组件及其管线信息（body、aim、noise、extensions）
- `unityCameras`：所有 Unity Camera 组件及其 depth 与 FOV
- `cinemachineInstalled`：Cinemachine 包是否可用

**配合使用：** 与 `manage_camera` 工具配合创建/配置相机

---

## 图形资源

### mcpforunity://scene/volumes

**用途：** 列出场景中所有 Volume 组件及其效果与参数。在使用 `manage_graphics` 的 volume 动作前建议先读取。

**返回：**
```json
{
  "pipeline": "Universal (URP)",
  "volumes": [
    {
      "name": "PostProcessVolume",
      "instance_id": -24600,
      "is_global": true,
      "weight": 1.0,
      "priority": 0,
      "blend_distance": 0,
      "profile": "MyProfile",
      "profile_path": "Assets/Settings/MyProfile.asset",
      "effects": [
        {
          "type": "Bloom",
          "active": true,
          "overridden_params": ["intensity", "threshold", "scatter"]
        },
        {
          "type": "Vignette",
          "active": true,
          "overridden_params": ["intensity", "smoothness"]
        }
      ]
    }
  ]
}
```

**关键字段：**
- `is_global`：该 volume 是全局生效，还是仅在碰撞器范围内生效
- `effects[].overridden_params`：当前被显式覆盖（非默认值）的参数
- `profile_path`：内嵌 profile 为空字符串；共享 profile 为资源路径

**配合使用：** 与 `manage_graphics` 的 volume 动作配合（volume_create、volume_add_effect、volume_set_effect 等）

### mcpforunity://rendering/stats

**用途：** 当前渲染性能计数器（draw calls、batches、triangles、memory）。

**返回：**
```json
{
  "draw_calls": 42,
  "batches": 35,
  "set_pass_calls": 12,
  "triangles": 15234,
  "vertices": 8456,
  "dynamic_batches": 5,
  "static_batches": 20,
  "shadow_casters": 3,
  "render_textures": 8,
  "render_textures_bytes": 16777216,
  "visible_skinned_meshes": 2
}
```

**配合使用：** 与 `manage_graphics` 的统计动作配合（stats_get、stats_list_counters、stats_get_memory）

### mcpforunity://pipeline/renderer-features

**用途：** 当前激活渲染器上的 URP renderer features（SSAO、Decals 等）。

**返回：**
```json
{
  "rendererDataName": "PC_Renderer",
  "features": [
    {
      "index": 0,
      "name": "ScreenSpaceAmbientOcclusion",
      "type": "ScreenSpaceAmbientOcclusion",
      "isActive": true,
      "properties": { "m_Settings": "Generic" }
    }
  ]
}
```

**关键字段：**
- `index`：在 feature 列表中的位置（用于 feature_toggle、feature_remove、feature_configure）
- `isActive`：该 feature 是否启用
- `rendererDataName`：当前激活的是哪个 URP renderer data 资源

**配合使用：** 与 `manage_graphics` 的 feature 动作配合（feature_list、feature_add、feature_remove、feature_toggle 等）

---

## 场景与 GameObject 资源

### mcpforunity://scene/gameobject-api

**用途：** GameObject 资源文档（建议先读）。

### mcpforunity://scene/gameobject/{instance_id}

**用途：** GameObject 基础数据（元信息，不含组件属性）。

**参数：**
- `instance_id` (int)：来自 `find_gameobjects` 的 GameObject 实例 ID

**返回：**
```json
{
  "instanceID": 12345,
  "name": "Player",
  "tag": "Player",
  "layer": 8,
  "layerName": "Player",
  "active": true,
  "activeInHierarchy": true,
  "isStatic": false,
  "transform": {
    "position": [0, 1, 0],
    "rotation": [0, 0, 0],
    "scale": [1, 1, 1]
  },
  "parent": {"instanceID": 0},
  "children": [{"instanceID": 67890}],
  "componentTypes": ["Transform", "Rigidbody", "PlayerController"],
  "path": "/Player"
}
```

### mcpforunity://scene/gameobject/{instance_id}/components

**用途：** 所有组件及其完整属性序列化（分页）。

**参数：**
- `instance_id` (int)：GameObject 实例 ID
- `page_size` (int)：默认 25，最大 100
- `cursor` (int)：分页游标
- `include_properties` (bool)：默认 true，设为 false 仅返回类型

**返回：**
```json
{
  "gameObjectID": 12345,
  "gameObjectName": "Player",
  "components": [
    {
      "type": "Transform",
      "properties": {
        "position": {"x": 0, "y": 1, "z": 0},
        "rotation": {"x": 0, "y": 0, "z": 0, "w": 1}
      }
    },
    {
      "type": "Rigidbody",
      "properties": {
        "mass": 1.0,
        "useGravity": true
      }
    }
  ],
  "cursor": 0,
  "pageSize": 25,
  "nextCursor": null,
  "hasMore": false
}
```

### mcpforunity://scene/gameobject/{instance_id}/component/{component_name}

**用途：** 单个组件及其完整属性。

**参数：**
- `instance_id` (int)：GameObject 实例 ID
- `component_name` (string)：例如 `"Rigidbody"`、`"Camera"`、`"Transform"`

**返回：**
```json
{
  "gameObjectID": 12345,
  "gameObjectName": "Player",
  "component": {
    "type": "Rigidbody",
    "properties": {
      "mass": 1.0,
      "drag": 0,
      "angularDrag": 0.05,
      "useGravity": true,
      "isKinematic": false
    }
  }
}
```

---

## Prefab 资源

### mcpforunity://prefab-api

**用途：** Prefab 资源文档。

### mcpforunity://prefab/{encoded_path}

**用途：** Prefab 资源信息。

**参数：**
- `encoded_path` (string)：URL 编码路径，例如 `Assets%2FPrefabs%2FPlayer.prefab`

**路径编码：**
```
Assets/Prefabs/Player.prefab → Assets%2FPrefabs%2FPlayer.prefab
```

**返回：**
```json
{
  "assetPath": "Assets/Prefabs/Player.prefab",
  "guid": "abc123...",
  "prefabType": "Regular",
  "rootObjectName": "Player",
  "rootComponentTypes": ["Transform", "PlayerController"],
  "childCount": 5,
  "isVariant": false,
  "parentPrefab": null
}
```

### mcpforunity://prefab/{encoded_path}/hierarchy

**用途：** 完整 prefab 层级（包含嵌套 prefab 信息）。

**返回：**
```json
{
  "prefabPath": "Assets/Prefabs/Player.prefab",
  "total": 6,
  "items": [
    {
      "name": "Player",
      "instanceId": 12345,
      "path": "/Player",
      "activeSelf": true,
      "childCount": 2,
      "componentTypes": ["Transform", "PlayerController"]
    },
    {
      "name": "Model",
      "path": "/Player/Model",
      "isNestedPrefab": true,
      "nestedPrefabPath": "Assets/Prefabs/PlayerModel.prefab"
    }
  ]
}
```

---

## 项目资源

### mcpforunity://project/info

**用途：** 静态项目配置。

**返回：**
```json
{
  "projectRoot": "/Users/dev/MyProject",
  "projectName": "MyProject",
  "unityVersion": "2022.3.10f1",
  "platform": "StandaloneWindows64",
  "assetsPath": "/Users/dev/MyProject/Assets"
}
```

### mcpforunity://project/tags

**用途：** TagManager 中定义的全部 tag。

**返回：**
```json
["Untagged", "Respawn", "Finish", "EditorOnly", "MainCamera", "Player", "GameController", "Enemy"]
```

### mcpforunity://project/layers

**用途：** 所有 layer 及其索引（0-31）。

**返回：**
```json
{
  "0": "Default",
  "1": "TransparentFX",
  "2": "Ignore Raycast",
  "4": "Water",
  "5": "UI",
  "8": "Player",
  "9": "Enemy"
}
```

### mcpforunity://menu-items

**用途：** 所有可用的 Unity 菜单项。

**返回：**
```json
[
  "File/New Scene",
  "File/Open Scene",
  "File/Save",
  "Edit/Undo",
  "Edit/Redo",
  "GameObject/Create Empty",
  "GameObject/3D Object/Cube",
  "Window/General/Console"
]
```

### mcpforunity://custom-tools

**用途：** 当前 Unity 项目中可用的自定义工具。

**返回：**
```json
{
  "project_id": "MyProject",
  "tool_count": 3,
  "tools": [
    {
      "name": "capture_screenshot",
      "description": "Capture screenshots in Unity",
      "parameters": [
        {"name": "filename", "type": "string", "required": true},
        {"name": "width", "type": "int", "required": false},
        {"name": "height", "type": "int", "required": false}
      ]
    }
  ]
}
```

---

## 实例资源

### mcpforunity://instances

**用途：** 所有正在运行的 Unity Editor 实例（用于多实例工作流）。

**返回：**
```json
{
  "transport": "http",
  "instance_count": 2,
  "instances": [
    {
      "id": "MyProject@abc123",
      "name": "MyProject",
      "hash": "abc123",
      "unity_version": "2022.3.10f1",
      "connected_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "TestProject@def456",
      "name": "TestProject",
      "hash": "def456",
      "unity_version": "2022.3.10f1",
      "connected_at": "2024-01-15T11:00:00Z"
    }
  ],
  "warnings": []
}
```

**配合使用：** `set_active_instance(instance="MyProject@abc123")`

---

## 测试资源

### mcpforunity://tests

**用途：** 项目中的全部测试。

**返回：**
```json
[
  {
    "name": "TestSomething",
    "full_name": "MyTests.TestSomething",
    "mode": "EditMode"
  },
  {
    "name": "TestOther",
    "full_name": "MyTests.TestOther",
    "mode": "PlayMode"
  }
]
```

### mcpforunity://tests/{mode}

**用途：** 按模式过滤后的测试。

**参数：**
- `mode` (string)：`"EditMode"` 或 `"PlayMode"`

**示例：** `mcpforunity://tests/EditMode`

---

## 最佳实践

### 1. 先检查编辑器状态

```python
# Before any complex operation:
# Read mcpforunity://editor/state
# Check ready_for_tools == true
```

### 2. 先查找再读取的模式

```python
# 1. find_gameobjects to get IDs
result = find_gameobjects(search_term="Player")

# 2. Read resource for full data
# mcpforunity://scene/gameobject/{id}
```

### 3. 大查询使用分页

```python
# Start with include_properties=false for component lists
# mcpforunity://scene/gameobject/{id}/components?include_properties=false&page_size=25

# Then read specific components as needed
# mcpforunity://scene/gameobject/{id}/component/Rigidbody
```

### 4. Prefab 路径必须 URL 编码

```python
# Wrong:
# mcpforunity://prefab/Assets/Prefabs/Player.prefab

# Correct:
# mcpforunity://prefab/Assets%2FPrefabs%2FPlayer.prefab
```

### 5. 多实例意识

```python
# Always check mcpforunity://instances when:
# - First connecting
# - Commands fail unexpectedly
# - Working with multiple projects
```
