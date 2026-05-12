# Stage Tamagotchi Godot C# 开发方法

本指南仅适用于 `engines/stage-tamagotchi-godot`。

它定义该 Godot engine 中 C# 代码应如何组织，以及现代 C# 功能应如何使用。格式化和命名规则属于次级内容，位于本地 `.editorconfig` 和 `docs/csharp-style.md`。

## 1. 范围

以下内容适用本指南：

- Godot scene scripts。
- 运行时 coordinators 和 controllers。
- host-stage transport contracts。
- registry 和 discovery 代码。
- 该 engine 内的 tooling 和 editor-support 代码。

不要把本指南当作整个仓库的 C# 标准。

## 2. 分层模型

编写实现前，先把 engine C# 代码拆成以下层：

1. Scene Script：Godot 拥有的 `Node` 或 `Node3D` partial class、生命周期入口和 scene binding。
2. Runtime Core：普通 C# 运行时逻辑，包括 controllers、coordinators、state holders、services。
3. Contract and Transport：消息类型、settings snapshots、ready/fatal/shutdown/state-update payloads。
4. Registry and Discovery：descriptors、启动期 discovery、catalogues 和 lookup tables。
5. Tooling and Editor Support：面向 inspector 的 helpers、import/export helpers、debug 或 editor-only 数据组装。

默认不要把这些职责压进单个 Godot script。

## 3. Scene Script 规则

Scene script 应保持轻量。

适合放入 scene script 的内容：

- Godot 生命周期入口，例如 `_Ready`。
- 节点查找和 scene wiring。
- 将控制权交给 runtime objects。
- 将 Godot callbacks 桥接到显式 runtime code。

除非代码非常简单，否则避免把以下内容直接放进 scene script：

- transport protocol handling。
- registry construction。
- 复杂状态转换。
- business 或 gameplay rules。
- 大型数据转换 pipeline。

如果一个 scene script 同时拥有生命周期、运行时状态、协议处理和工具配置，请拆分代码。

## 4. Runtime Core 规则

优先把持久运行时逻辑放入普通 C# 对象。

优先使用：

- 小型 coordinator，而不是无所不知的大类。
- 显式 state object，而不是隐藏的 mutable flags。
- 通过构造函数或方法注入依赖。
- 清晰调用流，而不是隐式控制转移。

Runtime core 代码应易于在 debugger 中追踪。优先使用显式 map、state 和 control flow，而不是聪明抽象。

## 5. Contract and Transport 规则

跨边界通信应由类型驱动。

以下内容优先使用显式类型：

- transport messages。
- payloads。
- settings snapshots。
- descriptors。
- registry entries。
- runtime state snapshots。

避免：

- 默认使用 `Dictionary<string, object?>` 作为 contract 形状。
- magic-string protocols 分散在多个文件中。
- anonymous objects 跨 subsystem 边界传递。
- 用注释替代真实类型定义。

规则很简单：先用类型定义边界，再围绕这些类型实现 transport。

## 6. Reflection 和 LINQ 策略

Reflection 用于 discovery，不用于 execution。

适合使用 reflection 的场景：启动期 module discovery、attribute metadata 读取、descriptor 生成、editor 或 tooling 支持。

不要在 per-frame logic、runtime hot-path dispatch、核心 state-machine execution 或稳定运行期的重复 dynamic invocation 中使用 reflection。

LINQ 适合 cold-path 查询和数据塑形，例如构建 registries、过滤 descriptors、配置投影、debug 或 tooling views。

避免在 hot paths、per-frame loops 或反复执行的运行时查询中使用重 LINQ；如果显式 index 或 dictionary 更清晰、更便宜，请使用它们。

心智模型：

- reflection 构建 catalogue。
- LINQ 塑形并查询 catalogue。
- runtime 通过显式结构执行。

## 7. Async 边界策略

在 I/O 和进程边界使用 async。

适合 async 的边界：socket 和 transport setup、文件 I/O、host-side process interaction、天然异步的启动加载。

避免把 async 推入 per-frame updates、核心 runtime loops 或应保持显式的 timing-sensitive behavior。

不要用 async 隐藏生命周期或顺序问题。

## 8. 延后决定

以下内容刻意延后，不应猜测：

- nullable reference type rollout policy。
- namespace strategy。
- `record` 使用边界。
- `required` member 使用边界。
- primary constructor 使用边界。
- helper-layer 与 scene-script 的功能允许边界。

当其中某项变得相关时，应明确决策并加入 engine-local guidance，而不是从 style tools 中推断。
