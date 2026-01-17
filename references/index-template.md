---
description: Code Context Index
alwaysApply: true
---
# {project_name} context index
> 按需加载以减少上下文占用

## 概览

| 属性         | 值             |
| ------------ | -------------- |
| **名称**     | {project_name} |
| **主语言**   | {languages}    |
| **框架**     | {frameworks}   |
| **文件数**   | {total_files}  |
| **代码行数** | ~{total_lines} |

## 核心入口点

- `{entry_path}` - {entry_description}
...

## 上下文详情

| 文件                                                     | 用途                   |
| -------------------------------------------------------- | ---------------------- |
| [project-overview.md](./context/project-overview.md)     | 项目概览、结构、入口点 |
| [task-recipes.md](./context/task-recipes.md)             | 常见任务路径           |
| [conventions.md](./context/conventions.md)               | 代码约定和规范         |
| [danger-zones.md](./context/danger-zones.md)             | 危险区域和敏感操作     |
| [context-boundaries.md](./context/context-boundaries.md) | 上下文边界             |
| [impact-analysis.md](./context/impact-analysis.md)       | 改动影响图             |

## 使用方式

1. **首次接触项目** → 加载 `project-overview.md`
2. **执行开发任务** → 加载 `task-recipes.md` + `conventions.md`
3. **修改代码前** → 加载 `danger-zones.md` + `impact-analysis.md`
4. **按功能开发** → 加载 `context-boundaries.md` 确定关注范围
5. **更新上下文** → 使用 `/update-code-context` 命令更新上下文
