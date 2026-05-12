# Stage Tamagotchi Godot C# 风格

这是次级格式化和命名参考。

请先阅读 `docs/csharp-development-method.md`，了解结构、分层和功能使用指导。本文件只用于低层代码风格。

本规范仅适用于 `engines/stage-tamagotchi-godot`。

它是该 Godot engine 的简单 C# 代码风格基线，不定义运行时结构、nullable 策略、namespace 策略或更广泛的架构规则。

## 基线

- Microsoft：通用 C# 代码约定。
- Microsoft：.NET 代码风格规则选项。
- Godot：C# 风格指南。

## 规则

- 使用 4 个空格。
- 使用 LF 行尾。
- 使用 UTF-8。
- 实际可行时，将行宽保持在 100 列以内。
- 使用 Allman 大括号风格。
- 先放 `System.*` using，再按字母序排序其余 using。
- 优先使用 C# 关键字类型，例如 `string`、`int`、`bool`。
- 只有当右侧能明显体现类型时才使用 `var`。
- 类型和成员使用 `PascalCase`。
- 局部变量和参数使用 `camelCase`。
- 私有字段使用 `_camelCase`。
- 移除未使用的 `using`。
- 修改文件时移除 Godot 模板注释。
- 修改文件时移除空生命周期方法，除非它们是有意保留的。
- 保持 `using` 显式。不要为该 engine 启用 implicit usings。

## 不在范围内

以下内容刻意不在本文件中决定：

- 运行时分层和设计方法。
- Nullable reference types。
- Namespace 策略。
- `record`、`required` 和 primary constructors。
- DTO 或 helper 专用风格规则。

## 验证

修改 C# 文件或本地 `.editorconfig` 后，请在 engine 目录中验证：

```powershell
dotnet format --verify-no-changes
```
