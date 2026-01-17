# Code Context Engineering

[中文](./README.md) | **English**

**Code Context Engineering** is a codebase analysis and context generation toolset designed specifically for AI Agents. It aims to help Agents quickly understand large project structures, code logic, and dependencies to generate high-quality context information.

## 🚀 Key Features

This project provides a powerful static analysis tool `scripts/analyze_project.py` with the following capabilities:

- **Deep Structure Scan**: Recursively analyzes project directory structures, intelligently ignoring noise files (e.g., `node_modules`, `.git`).
- **Multi-language AST Analysis**: Deep parsing of syntax trees to extract key symbols like classes, functions, interfaces, and decorators.
- **Dependency Graph**:
    - Automatically detects internal module import relationships.
    - Identifies project-level Circular Dependencies.
- **Standardized Output**: Generates structured Markdown reports ready for AI context injection.

## 🛠️ Quick Start

### Requirements
- Python 3.8+

### Usage

Basic Usage (Analyze current directory):
```bash
python3 scripts/analyze_project.py . -o analysis.md
```

Advanced Usage:
```bash
# Specify scan depth (default 10)
python3 scripts/analyze_project.py . --depth 5

# Analyze specific languages only
python3 scripts/analyze_project.py . --extensions py ts go
```

## 🧩 Supported Languages

The analyzer includes built-in advanced parsers for:

| Language                  | Capabilities                                                                 |
| :------------------------ | :--------------------------------------------------------------------------- |
| **Python**                | Classes, Functions, Decorators (via `ast`)                                   |
| **JavaScript/TypeScript** | Classes, Functions, Arrow Functions, Interfaces, Imports/Exports (via Regex) |
| **Go**                    | Structs, Interfaces, Functions                                               |
| **Rust**                  | Structs, Enums, Traits, Impls                                                |
| **C++**                   | Classes, Structs, Template Functions                                         |
| **PHP**                   | Classes, Interfaces, Traits                                                  |

## 📂 Project Structure

- **`scripts/`**: Core toolset.
    - `analyze_project.py`: Analyzer entry point.
    - `analyzer/`: Analysis engine logic and parsers.
- **`references/`**: Standard templates for context engineering (e.g., Agreements, Boundaries).
- **`.agent/skills/`**: Extended skills library (Context Compression, Degradation, etc.).

## 📄 Protocols & Guides

For detailed context generation protocols, please refer to [SKILL.md](./SKILL.md).
