---
name: code-context-analyzer
description: Codebase static analysis tool for generating structured project metadata. Triggers: "analyze project", "understand codebase", "prepare context", "分析项目代码", "初始化上下文".
---

# Code Context Analyzer

Generate structured project metadata to help agents understand code and create context files.

## Quick Start

```bash
# 1. Analyze project
python3 scripts/analyze_project.py . -o .analysis.md

# 2. Generate context files in {context_dir} (see Agent Detection below)
# 3. Create index at {index_file}, then delete .analysis.md
```

> For detailed steps, see [Initialization Protocol](#1-initialization-protocol).


## Context Engineering Protocol

Agent **MUST** follow strictly defined protocols based on the user's intent. Do not skip steps.

### 1. Initialization Protocol
**Trigger**: "Initialize context", "Analyze project", "First time setup"
**Goal**: Generate the **Full Context Suite**. DO NOT stop after just the overview.

**Execution Sequence**:
1.  **Analyze**: Generate `.analysis.md` with project metadata
    ```bash
    python3 scripts/analyze_project.py . -o .analysis.md
    ```
    > Options: `--depth N` (default: 10), `--extensions py js ts`
    
    **Output Schema** (sections in `.analysis.md`):
    | Section                            | Use In                                      |
    | :--------------------------------- | :------------------------------------------ |
    | Header, Dependencies, Entry Points | → `project-overview.md`                     |
    | Directory Structure, Code Symbols  | → `context-boundaries.md`, `conventions.md` |
    | Internal Dependencies              | → `impact-analysis.md`                      |
    | Circular Dependencies              | → `danger-zones.md`                         |
    
2.  **Language**: Generate context files in user's language. Default: Chinese.
3.  **Auto-Detection**: Check which config directories exist in project root:
    ```
    .cursor/ → Cursor    |  .windsurf/ → Windsurf  |  .claude/ → ClaudeCode
    .agent/  → Antigravity|  .codex/    → Codex     |  (none)   → Ask user
    ```
    If multiple exist, prefer the one matching current runtime environment.
    
    **Tool-Specific Paths**:
    | Agent       | `agent_workspace` | `context_dir`                | `index_file`                              |
    | :---------- | :---------------- | :--------------------------- | :---------------------------------------- |
    | Cursor      | `.cursor`         | `.cursor/rules/context/`     | `.cursor/rules/code-context.mdc`          |
    | Windsurf    | `.windsurf`       | `.windsurf/context/`         | `.windsurf/rules/code-context.md`         |
    | ClaudeCode  | `.claude`         | `.claude/context/`           | `CLAUDE.md` (project root)                |
    | Antigravity | `.agent`          | `.agent/context/`            | `.agent/rules/code-context.md`            |
    | Codex       | `.codex`          | `.codex/context/`            | `AGENTS.md` (project root)                |
    | Other       | `{user_input}`    | `{agent_workspace}/context/` | `{agent_workspace}/rules/code-context.md` |

4.  **Generate Core Suite** (Mandatory):
    > **Data Sources**: `.analysis.md` (machine data) + `references/*.md` (templates)
    > **Output Location**: `{context_dir}` from step 3
    
    | Phase            | Output File             | Data Source                        | Content Strategy                      |
    | :--------------- | :---------------------- | :--------------------------------- | :------------------------------------ |
    | A. Understanding | `project-overview.md`   | Header, Dependencies, Entry Points | Facts: stats, tech stack, structure   |
    | B. Architecture  | `context-boundaries.md` | Directory Structure, Code Symbols  | Map: features/modules by folder       |
    | C. Agreements    | `conventions.md`        | Code Symbols (patterns)            | Rules: naming, style, patterns        |
    | C. Agreements    | `task-recipes.md`       | Entry Points, config files         | Actions: build, test, deploy commands |
    | D. Safety        | `danger-zones.md`       | Circular Dependencies              | Risks: complex logic, legacy code     |
    | D. Safety        | `impact-analysis.md`    | Internal Dependencies              | Relationships: import/export flow     |

5.  **Quality Gate (Self-Correction)**:
    *   **Review**: Check each generated file for substance.
    *   **Prune**: If a file contains only generic text, placeholders, or "no issues found", **DELETE IT**. No file is better than a noise file.
6.  **Finalize**:
    *   Create index at `{index_file}` using `references/index-template.md` as structure guide.
    *   **IMPORTANT**: Remove links to any deleted files from the index.
    *   Delete `.analysis.md` (cleanup intermediate file).

### 2. Maintenance Protocol
**Trigger**: "Update context", "I added a new feature", "Refactored code"
**Goal**: Update ONLY the affected documents to minimize noise.

*   **Structure Change** (New files/folders) -> Update `project-overview.md` & `context-boundaries.md`
*   **New Dependencies** -> Update `project-overview.md` & `impact-analysis.md`
*   **Process Change** -> Update `conventions.md` or `task-recipes.md`

### 3. Template Reference

All templates are in `references/` directory:

| Template File                    | Purpose                             |
| :------------------------------- | :---------------------------------- |
| `project-overview-template.md`   | Project facts and stats             |
| `context-boundaries-template.md` | Module/feature boundaries           |
| `conventions-template.md`        | Code style and naming rules         |
| `task-recipes-template.md`       | Common commands (build/test/deploy) |
| `danger-zones-template.md`       | Risk areas and legacy code          |
| `impact-analysis-template.md`    | Dependency relationships            |
| `index-template.md`              | Root index file structure           |

## Reference

Templates are located in `references/` directory relative to this skill file.

See [scripts/analyze_project.py](./scripts/analyze_project.py) for implementation details.

**Version**: 1.2.0
**Last Updated**: 2026-01-18
