---
name: code-context-analyzer
description: Comprehensive codebase static analysis tool for generating structured project metadata. Triggers on: (1) exploring new/unfamiliar codebases, (2) analyzing project architecture and dependencies, (3) preparing context for AI agents. key trigger phrases: "analyze project structure", "understand codebase", "generate project report", "prepare AI context". Chinese triggers: "分析项目代码" (analyze project code), "初始化上下文" (initialize context), "理解项目上下文" (understand project context), "生成项目报告".
---

# Code Context Analyzer

Generate structured project metadata to help agents understand code and create context files.

## Tool Usage

`analyze_project.py` is a static analysis tool.

### Commands

```bash
python3 analyze_project.py /path/to/project -o .analysis.md
python3 analyze_project.py /path/to/project --depth 10
python3 analyze_project.py /path/to/project --extensions py js
```

### Data Schema (.analysis.md)

| Section                 | Description                                      |
| :---------------------- | :----------------------------------------------- |
| `Header`                | Project Metadata (Name, Root, Type, Stats)       |
| `Directory Structure`   | Tree view of folders (limited by depth)          |
| `Code Symbols`          | List of classes, functions, and symbols per file |
| `Internal Dependencies` | (Inferred) Internal import relationships         |

## Context Engineering Protocol

Agent **MUST** follow strictly defined protocols based on the user's intent. Do not skip steps.

### 1. Initialization Protocol
**Trigger**: "Initialize context", "Analyze project", "First time setup"
**Goal**: Generate the **Full Context Suite**. DO NOT stop after just the overview.

**Execution Sequence**:
1.  **Analyze**: Run `python3 scripts/analyze_project.py . -o .analysis.md --depth <project_max_depth> --extensions <custom_extensions>`
2.  **Language**: Using user's language to generate context files. Default in Chinese.
3.  **Confirm Agent Workspace**:
    *   **Cursor** -> agent_workspace = .cursor
    *   **Windsurf** -> agent_workspace = .windsurf
    *   **Codex** -> agent_workspace = .codex
    *   **ClaudeCode** -> agent_workspace = .claude
    *   **Antigravity** -> agent_workspace = .agent
    *   **Other** -> agent_workspace = {user_input}
4.  **Generate Core Suite** (Mandatory):
    *   **Phase A: Understanding** -> Create `{agent_workspace}/context/project-overview.md`
    *   **Phase B: Architecture** -> Create `{agent_workspace}/context/context-boundaries.md`
    *   **Phase C: Agreements** -> Create `{agent_workspace}/context/conventions.md` & `{agent_workspace}/context/task-recipes.md`
    *   **Phase D: Safety** -> Create `{agent_workspace}/context/danger-zones.md` & `{agent_workspace}/context/impact-analysis.md`
5.  **Quality Gate (Self-Correction)**:
    *   **Review**: Briefly check content of generated files.
    *   **Prune**: If a file (e.g., `danger-zones.md`) contains only generic text, placeholders, or "no issues found", **DELETE IT**. It is better to have no file than a noise file.
6.  **Finalize**:
    *   Create root index: `{agent_workspace}/rules/code-context.md` (using `references/index-template.md`).
    *   If agent from cursor, `code-context.md` change to `code-context.mdc`
    *   **IMPORTANT**: Update the index to **REMOVE links** to any files you deleted in the Prune step.
    *   Delete `.analysis.md` (cleanup).

### 2. Maintenance Protocol
**Trigger**: "Update context", "I added a new feature", "Refactored code"
**Goal**: Update ONLY the affected documents to minimize noise.

*   **Structure Change** (New files/folders) -> Update `project-overview.md` & `context-boundaries.md`
*   **New Dependencies** -> Update `project-overview.md` & `impact-analysis.md`
*   **Process Change** -> Update `conventions.md` or `task-recipes.md`

### 3. Template Mapping Reference

| Target File             | Template Source                  | Content Strategy                                                              |
| :---------------------- | :------------------------------- | :---------------------------------------------------------------------------- |
| `project-overview.md`   | `project-overview-template.md`   | **Objective**: Facts. Use JSON data for stats/stack.                          |
| `context-boundaries.md` | `context-boundaries-template.md` | **Objective**: Map. Define features/modules by folder structure.              |
| `conventions.md`        | `conventions-template.md`        | **Objective**: Rules. Infer code style, naming, patterns from code.           |
| `danger-zones.md`       | `danger-zones-template.md`       | **Objective**: Risks. Identify complex logic, legacy code, security hotspots. |
| `task-recipes.md`       | `task-recipes-template.md`       | **Objective**: Actions. Define standard commands (build, test, deploy).       |
| `impact-analysis.md`    | `impact-analysis-template.md`    | **Objective**: Relationships. Map imports/exports to see dependency flow.     |

## Reference

See [scripts/analyze_project.py](./scripts/analyze_project.py) for implementation details.

**Version**: 1.1.0
**Last Updated**: 2026-01-17
