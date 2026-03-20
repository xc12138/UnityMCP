# ProBuilder 工作流指南

通过 MCP for Unity 进行 AI 驱动 ProBuilder 网格编辑的实践模式与最佳实践。

## 可用性

ProBuilder 是一个**可选**的 Unity 包（`com.unity.probuilder`）。在使用任何 ProBuilder 工具前，请先检查 `mcpforunity://project/info` 或调用 `manage_probuilder(action="ping")` 确认已安装。若可用，对于需要编辑、多材质面或较复杂形体的几何体，**优先使用 ProBuilder 而非 primitive GameObject**。

## 核心流程：始终先获取信息

在进行任何网格编辑前，先调用 `get_mesh_info`（`include='faces'`）以理解当前几何结构：

```python
# Step 1: Get face info with directions
result = manage_probuilder(action="get_mesh_info", target="MyCube",
    properties={"include": "faces"})

# Response includes per-face:
#   index: 0, normal: [0, 1, 0], center: [0, 0.5, 0], direction: "top"
#   index: 1, normal: [0, -1, 0], center: [0, -0.5, 0], direction: "bottom"
#   index: 2, normal: [0, 0, 1], center: [0, 0, 0.5], direction: "front"
#   ...

# Step 2: Use the direction labels to pick faces
# Want to extrude the top? Find the face with direction="top"
manage_probuilder(action="extrude_faces", target="MyCube",
    properties={"faceIndices": [0], "distance": 1.5})
```

### Include 参数

| 取值 | 返回内容 | 适用场景 |
|-------|---------|----------|
| `"summary"` | 数量、包围盒、材质 | 快速检查 / 校验 |
| `"faces"` | + 法线、中心点、方向 | 选择待编辑的面 |
| `"edges"` | + 边顶点对及世界坐标（最多 200） | 基于边的操作 |
| `"all"` | 全部信息 | 完整网格分析 |

## 形体创建

### 全部 12 种形体类型

```python
# Basic shapes
manage_probuilder(action="create_shape", properties={"shape_type": "Cube", "name": "MyCube"})
manage_probuilder(action="create_shape", properties={"shape_type": "Sphere", "name": "MySphere"})
manage_probuilder(action="create_shape", properties={"shape_type": "Cylinder", "name": "MyCyl"})
manage_probuilder(action="create_shape", properties={"shape_type": "Plane", "name": "MyPlane"})
manage_probuilder(action="create_shape", properties={"shape_type": "Cone", "name": "MyCone"})
manage_probuilder(action="create_shape", properties={"shape_type": "Prism", "name": "MyPrism"})

# Parametric shapes
manage_probuilder(action="create_shape", properties={
    "shape_type": "Torus", "name": "MyTorus",
    "rows": 16, "columns": 24, "innerRadius": 0.5, "outerRadius": 1.0
})
manage_probuilder(action="create_shape", properties={
    "shape_type": "Pipe", "name": "MyPipe",
    "radius": 1.0, "height": 2.0, "thickness": 0.2
})
manage_probuilder(action="create_shape", properties={
    "shape_type": "Arch", "name": "MyArch",
    "radius": 2.0, "angle": 180, "segments": 12
})

# Architectural shapes
manage_probuilder(action="create_shape", properties={
    "shape_type": "Stair", "name": "MyStairs", "steps": 10
})
manage_probuilder(action="create_shape", properties={
    "shape_type": "CurvedStair", "name": "Spiral", "steps": 12
})
manage_probuilder(action="create_shape", properties={
    "shape_type": "Door", "name": "MyDoor"
})

# Custom polygon
manage_probuilder(action="create_poly_shape", properties={
    "points": [[0,0,0], [5,0,0], [5,0,5], [2.5,0,7], [0,0,5]],
    "extrudeHeight": 3.0, "name": "Pentagon"
})
```

## 常见编辑操作

### 挤出屋顶

```python
# 1. Create a building base
manage_probuilder(action="create_shape", properties={
    "shape_type": "Cube", "name": "Building", "size": [4, 3, 6]
})

# 2. Find the top face
info = manage_probuilder(action="get_mesh_info", target="Building",
    properties={"include": "faces"})
# Find face with direction="top" -> e.g. index 2

# 3. Extrude upward for a flat roof extension
manage_probuilder(action="extrude_faces", target="Building",
    properties={"faceIndices": [2], "distance": 0.5})
```

### 开孔（删除面）

```python
# 1. Get face info
info = manage_probuilder(action="get_mesh_info", target="Wall",
    properties={"include": "faces"})
# Find the face with direction="front" -> e.g. index 4

# 2. Subdivide to create more faces
manage_probuilder(action="subdivide", target="Wall",
    properties={"faceIndices": [4]})

# 3. Get updated face info (indices changed after subdivide!)
info = manage_probuilder(action="get_mesh_info", target="Wall",
    properties={"include": "faces"})

# 4. Delete the center face(s) for the hole
manage_probuilder(action="delete_faces", target="Wall",
    properties={"faceIndices": [6]})
```

### 边倒角

```python
# Get edge info
info = manage_probuilder(action="get_mesh_info", target="MyCube",
    properties={"include": "edges"})

# Bevel specific edges
manage_probuilder(action="bevel_edges", target="MyCube",
    properties={"edgeIndices": [0, 1, 2, 3], "amount": 0.1})
```

### 分离面到新对象

```python
# Detach and keep original (default)
manage_probuilder(action="detach_faces", target="MyCube",
    properties={"faceIndices": [0, 1], "deleteSourceFaces": False})

# Detach and remove from source
manage_probuilder(action="detach_faces", target="MyCube",
    properties={"faceIndices": [0, 1], "deleteSourceFaces": True})
```

### 按方向选择面

```python
# Select all upward-facing faces
manage_probuilder(action="select_faces", target="MyMesh",
    properties={"direction": "up", "tolerance": 0.7})

# Grow selection from a seed face
manage_probuilder(action="select_faces", target="MyMesh",
    properties={"growFrom": [0], "growAngle": 45})
```

### 双面几何体

```python
# Create inside faces for a room (duplicate and flip normals)
manage_probuilder(action="duplicate_and_flip", target="Room",
    properties={"faceIndices": [0, 1, 2, 3, 4, 5]})
```

### 从已有顶点创建多边形

```python
# Connect existing vertices into a new face (auto-finds winding order)
manage_probuilder(action="create_polygon", target="MyMesh",
    properties={"vertexIndices": [0, 3, 7, 4]})
```

## 顶点操作

```python
# Move vertices by offset
manage_probuilder(action="move_vertices", target="MyCube",
    properties={"vertexIndices": [0, 1, 2, 3], "offset": [0, 1, 0]})

# Weld nearby vertices (proximity-based merge)
manage_probuilder(action="weld_vertices", target="MyCube",
    properties={"vertexIndices": [0, 1, 2, 3], "radius": 0.1})

# Insert vertex on an edge
manage_probuilder(action="insert_vertex", target="MyCube",
    properties={"edge": {"a": 0, "b": 1}, "point": [0.5, 0, 0]})

# Add evenly-spaced points along edges
manage_probuilder(action="append_vertices_to_edge", target="MyCube",
    properties={"edgeIndices": [0, 1], "count": 3})
```

## 平滑工作流

### 自动平滑（推荐默认）

```python
# Apply auto-smoothing with default 30 degree threshold
manage_probuilder(action="auto_smooth", target="MyMesh",
    properties={"angleThreshold": 30})
```

- **低角度（15-25）**：硬边更多，棱面感更强
- **中角度（30-45）**：通用默认值，曲面平滑且保留锐角
- **高角度（60-80）**：整体更平滑，仅最锐利的边保持硬边

### 手动平滑组

```python
# Set specific faces to smooth group 1
manage_probuilder(action="set_smoothing", target="MyMesh",
    properties={"faceIndices": [0, 1, 2], "smoothingGroup": 1})

# Set other faces to hard edges (group 0)
manage_probuilder(action="set_smoothing", target="MyMesh",
    properties={"faceIndices": [3, 4, 5], "smoothingGroup": 0})
```

## 网格清理模式

编辑后请始终执行清理：

```python
# 1. Center the pivot (important after extrusions that shift geometry)
manage_probuilder(action="center_pivot", target="MyMesh")

# 2. Optionally freeze transform if you moved/rotated the object
manage_probuilder(action="freeze_transform", target="MyMesh")

# 3. Validate mesh health
result = manage_probuilder(action="validate_mesh", target="MyMesh")
# Check result.data.healthy -- if false, repair

# 4. Auto-repair if needed
manage_probuilder(action="repair_mesh", target="MyMesh")
```

## 使用 ProBuilder 构建复杂对象

当 ProBuilder 可用时，对于复杂几何体优先使用它而非 primitive GameObject。ProBuilder 支持创建、编辑、组合形体，无需外部 3D 工具即可搭建细节对象。

### 示例：简易房屋

```python
# 1. Create base building
manage_probuilder(action="create_shape", properties={
    "shape_type": "Cube", "name": "House", "width": 6, "height": 3, "depth": 8
})

# 2. Get face info to find the top face
info = manage_probuilder(action="get_mesh_info", target="House",
    properties={"include": "faces"})
# Find direction="top" -> e.g. index 2

# 3. Extrude the top face to create a flat raised section
manage_probuilder(action="extrude_faces", target="House",
    properties={"faceIndices": [2], "distance": 0.3})

# 4. Re-query faces, then move top vertices inward to form a ridge
info = manage_probuilder(action="get_mesh_info", target="House",
    properties={"include": "faces"})
# Find the new top face after extrude, get its vertex indices
# Move them to form a peaked roof shape
manage_probuilder(action="move_vertices", target="House",
    properties={"vertexIndices": [0, 1, 2, 3], "offset": [0, 2, 0]})

# 5. Cut a doorway: subdivide front face, delete center sub-face
info = manage_probuilder(action="get_mesh_info", target="House",
    properties={"include": "faces"})
# Find direction="front", subdivide it
manage_probuilder(action="subdivide", target="House",
    properties={"faceIndices": [4]})

# Re-query, find bottom-center face, delete it
info = manage_probuilder(action="get_mesh_info", target="House",
    properties={"include": "faces"})
manage_probuilder(action="delete_faces", target="House",
    properties={"faceIndices": [12]})

# 6. Add a door frame with arch
manage_probuilder(action="create_shape", properties={
    "shape_type": "Door", "name": "Doorway",
    "position": [0, 0, 4], "width": 1.5, "height": 2.5
})

# 7. Add stairs to the door
manage_probuilder(action="create_shape", properties={
    "shape_type": "Stair", "name": "FrontSteps",
    "position": [0, 0, 5], "steps": 3, "width": 2
})

# 8. Smooth organic parts, keep architectural edges sharp
manage_probuilder(action="auto_smooth", target="House",
    properties={"angleThreshold": 30})

# 9. Assign materials per face
manage_probuilder(action="set_face_material", target="House",
    properties={"faceIndices": [0, 1, 2, 3], "materialPath": "Assets/Materials/Brick.mat"})
manage_probuilder(action="set_face_material", target="House",
    properties={"faceIndices": [4, 5], "materialPath": "Assets/Materials/Roof.mat"})

# 10. Cleanup
manage_probuilder(action="center_pivot", target="House")
manage_probuilder(action="validate_mesh", target="House")
```

### 示例：带柱走廊（批量）

```python
# Create multiple columns efficiently
batch_execute(commands=[
    {"tool": "manage_probuilder", "params": {
        "action": "create_shape",
        "properties": {"shape_type": "Cylinder", "name": f"Pillar_{i}",
                       "radius": 0.3, "height": 4, "segments": 12,
                       "position": [i * 3, 0, 0]}
    }} for i in range(6)
] + [
    # Floor
    {"tool": "manage_probuilder", "params": {
        "action": "create_shape",
        "properties": {"shape_type": "Plane", "name": "Floor",
                       "width": 18, "height": 6, "position": [7.5, 0, 0]}
    }},
    # Ceiling
    {"tool": "manage_probuilder", "params": {
        "action": "create_shape",
        "properties": {"shape_type": "Plane", "name": "Ceiling",
                       "width": 18, "height": 6, "position": [7.5, 4, 0]}
    }},
])

# Bevel all pillar tops for decoration
for i in range(6):
    info = manage_probuilder(action="get_mesh_info", target=f"Pillar_{i}",
        properties={"include": "edges"})
    # Find top ring edges, bevel them
    manage_probuilder(action="bevel_edges", target=f"Pillar_{i}",
        properties={"edgeIndices": [0, 1, 2, 3], "amount": 0.05})

# Smooth the pillars
for i in range(6):
    manage_probuilder(action="auto_smooth", target=f"Pillar_{i}",
        properties={"angleThreshold": 45})
```

### 示例：自定义 L 形房间

```python
# Use polygon shape for non-rectangular footprint
manage_probuilder(action="create_poly_shape", properties={
    "points": [
        [0, 0, 0], [10, 0, 0], [10, 0, 6],
        [4, 0, 6], [4, 0, 10], [0, 0, 10]
    ],
    "extrudeHeight": 3.0,
    "name": "LRoom"
})

# Create inside faces for the room interior
info = manage_probuilder(action="get_mesh_info", target="LRoom",
    properties={"include": "faces"})
# Duplicate and flip all faces to make interior visible
all_faces = list(range(info["data"]["faceCount"]))
manage_probuilder(action="duplicate_and_flip", target="LRoom",
    properties={"faceIndices": all_faces})

# Cut a window: subdivide a wall face, delete center
# (follow the get_mesh_info -> subdivide -> get_mesh_info -> delete pattern)
```

### 示例：环面结 / 装饰圆环

```python
# Create a torus
manage_probuilder(action="create_shape", properties={
    "shape_type": "Torus", "name": "Ring",
    "innerRadius": 0.3, "outerRadius": 2.0,
    "rows": 24, "columns": 32
})

# Smooth it for organic look
manage_probuilder(action="auto_smooth", target="Ring",
    properties={"angleThreshold": 60})

# Assign metallic material
manage_probuilder(action="set_face_material", target="Ring",
    properties={"faceIndices": [], "materialPath": "Assets/Materials/Gold.mat"})
# Note: empty faceIndices = all faces
```

## 批量模式

在多步骤流程中使用 `batch_execute` 可减少往返调用：

```python
batch_execute(commands=[
    {"tool": "manage_probuilder", "params": {
        "action": "create_shape",
        "properties": {"shape_type": "Cube", "name": "Column1", "position": [0, 0, 0]}
    }},
    {"tool": "manage_probuilder", "params": {
        "action": "create_shape",
        "properties": {"shape_type": "Cube", "name": "Column2", "position": [5, 0, 0]}
    }},
    {"tool": "manage_probuilder", "params": {
        "action": "create_shape",
        "properties": {"shape_type": "Cube", "name": "Column3", "position": [10, 0, 0]}
    }},
])
```

## 已知限制

### 暂不可用

这些动作在 API 中存在，但由于已知问题暂时无法正确工作：

| 动作 | 问题 | 规避方案 |
|--------|-------|------------|
| `set_pivot` | 顶点位置在 `ToMesh()`/`RefreshMesh()` 后无法持久化。ProBuilder 重建网格时会覆盖 `positions` 的设置器结果。需要 `SetVertices(IList<Vertex>)` 或直接访问 `m_Positions` 字段。 | 改用 `center_pivot`，或通过 Transform 定位对象。 |
| `convert_to_probuilder` | `MeshImporter` 构造函数内部抛错。可能需要使用 ProBuilder 的编辑器专用 `ProBuilderize` API，而非运行时 `MeshImporter`。 | 不要转换现有网格，改用 `create_shape` 或 `create_poly_shape` 原生创建。 |

### 通用限制

- 面索引在编辑过程中**不稳定**——任何修改后都要重新查询 `get_mesh_info`
- `get_mesh_info` 中边数据最多返回 **200 条边**
- `get_mesh_info` 中面数据最多返回 **100 个面**
- `subdivide` 内部使用 `ConnectElements.Connect`（ProBuilder 无公开 `Subdivide` API），其行为是连接面中点，而非传统四边形细分

## 关键规则

1. **编辑前始终先执行 get_mesh_info**——面索引在编辑过程中不稳定
2. **修改后务必重新查询**——subdivide、extrude、delete 都会改变面索引
3. **使用方向标签**——不要猜面索引，使用 direction 字段
4. **编辑后做清理**——`center_pivot + validate` 是良好实践
5. **有机形体优先自动平滑**——30 度是不错的默认值
6. **优先 ProBuilder 而非 primitive**——当包可用且你需要可编辑几何体时
7. **使用 batch_execute**——用于创建多个形体或重复操作
8. **截图验证**——复杂编辑后使用 `manage_camera(action="screenshot", include_image=True)` 检查可视结果
