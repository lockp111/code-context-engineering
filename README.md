# Code Context Engineering

**中文** | [English](./README_EN.md)

**Code Context Engineering** 是一个专为 AI Agent 设计的代码库分析与上下文生成工具集。它旨在帮助 Agent 快速理解大型项目结构、代码逻辑和依赖关系，从而生成高质量的上下文信息。

## 🚀 核心功能

本项目提供了一个强大的静态分析工具 `scripts/analyze_project.py`，支持以下特性：

- **深度结构扫描**：递归分析项目目录结构，智能忽略干扰文件（如 `node_modules`, `.git`）。
- **多语言 AST 分析**：深入解析代码语法树，提取类、函数、接口、装饰器等关键符号。
- **依赖关系图谱**：
    - 自动检测内部模块导入关系。
    - 识别项目级循环依赖（Circular Dependencies）。
- **标准化输出**：生成结构化的 Markdown 报告，直接作为 AI 的上下文输入。

## 🛠️ 快速开始

### 环境要求
- Python 3.8+

### 使用方法

基础用法（分析当前目录）：
```bash
python3 scripts/analyze_project.py . -o analysis.md
```

高级用法：
```bash
# 指定扫描深度（默认 10）
python3 scripts/analyze_project.py . --depth 5

# 仅分析特定语言
python3 scripts/analyze_project.py . --extensions py ts go
```

## 🧩 支持语言

分析器内置了针对以下语言的高级解析器：

| 语言                      | 解析能力                                         |
| :------------------------ | :----------------------------------------------- |
| **Python**                | 类, 函数, 装饰器 (基于 `ast`)                    |
| **JavaScript/TypeScript** | 类, 函数, 箭头函数, 接口, 导入/导出 (基于 Regex) |
| **Go**                    | 结构体, 接口, 函数                               |
| **Rust**                  | 结构体, 枚举, Trait, Impl                        |
| **C++**                   | 类, 结构体, 模板函数                             |
| **PHP**                   | 类, 接口, Trait                                  |

## 📂 项目结构

- **`scripts/`**: 核心工具集。
    - `analyze_project.py`: 分析器入口。
    - `analyzer/`: 分析引擎核心逻辑与解析器。
- **`references/`**: 上下文工程标准模板（如 Agreements, Boundaries 等）。
- **`.agent/skills/`**: 扩展技能库（Context Compression, Degradation 等）。

## 📄 协议与指南

详细的上下文生成协议请参考 [SKILL.md](./SKILL.md)。
