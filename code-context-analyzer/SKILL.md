---
name: code-context-analyzer
description: Generate structured project context files through static code analysis. Use when asked to "analyze project", "understand codebase", "初始化上下文", or setting up context for a new codebase.
---

# Code Context Analyzer

Generate structured project metadata to help agents understand code and create context files.

## Requirements

- Python 3.8+
- No external dependencies (uses standard library only)

## Quick Start

```bash
# Analyze project and generate metadata
python3 scripts/analyze_project.py . -o .analysis.md
```

After analysis, the Agent will:
1. Detect agent type (Cursor/Windsurf/ClaudeCode/etc.)
2. Generate context files in `{context_dir}`
3. Create index at `{index_file}`
4. Delete `.analysis.md`

> For detailed steps, see [Initialization Protocol](#1-initialization-protocol).

## Context Engineering Protocol

Agent **MUST** follow strictly defined protocols based on the user's intent. Do not skip steps.

### 1. Initialization Protocol

**Trigger**: "Initialize context", "Analyze project", "First time setup"  
**Goal**: Generate the **Full Context Suite**. DO NOT stop after just the overview.

**Execution Sequence**:

1. **Analyze**: Generate `.analysis.md` with project metadata
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

2. **Language**: Generate context files in user's language. Default: Chinese.

3. **Auto-Detection**: Check which config directories exist in project root:
   ```
   .cursor/ → Cursor    |  .windsurf/ → Windsurf  |  .claude/ → ClaudeCode
   .agent/  → Antigravity|  .codex/    → Codex     |  (none)   → Ask user
   ```
   If multiple exist, prefer the one matching current runtime environment.
   
   **Tool-Specific Paths**:
   | Agent       | `context_dir`                | `index_file`                     |
   | :---------- | :--------------------------- | :------------------------------- |
   | Cursor      | `.cursor/context/`           | `.cursor/rules/code-context.mdc` |
   | Windsurf    | `.windsurf/context/`         | `.windsurf/rules/code-context.md`|
   | ClaudeCode  | `.claude/context/`           | `CLAUDE.md` (project root)       |
   | Antigravity | `.agent/context/`            | `.agent/rules/code-context.md`   |
   | Codex       | `.codex/context/`            | `AGENTS.md` (project root)       |
   | Other       | `{agent_workspace}/context/` | `{agent_workspace}/rules/code-context.md` |

4. **Generate Core Suite** (Mandatory):
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
   | E. Data          | `database-schema.md`    | SQL migration files (*.sql)        | DDL: aggregated final table structure |
   | F. Business      | `critical-flows.md`     | Code analysis + domain knowledge   | Workflows & state machines            |

5. **Quality Gate (Self-Correction)**:
   - **Review**: Check each generated file for substance.
   - **Prune**: If a file contains only generic text, placeholders, or "no issues found", **DELETE IT**. No file is better than a noise file.

6. **Finalize**:
   - Create index at `{index_file}` using `references/context-index-template.md` as structure guide.
   - **IMPORTANT**: Remove links to any deleted files from the index.
   - Delete `.analysis.md` (cleanup intermediate file).

### 2. Maintenance Protocol

**Trigger**: "Update context", "I added a new feature", "Refactored code"  
**Goal**: Update ONLY the affected documents to minimize noise.

| Change Type                        | Update Target                                    |
| :--------------------------------- | :----------------------------------------------- |
| Structure Change (New files/folders) | `project-overview.md` & `context-boundaries.md` |
| New Dependencies                   | `project-overview.md` & `impact-analysis.md`     |
| Process Change                     | `conventions.md` or `task-recipes.md`            |
| Database Change (New migration/DDL)| Re-aggregate all SQL → `database-schema.md`      |
| Flow Change (New workflow/state)   | `critical-flows.md` with new flow diagrams       |

### 3. Template Reference

All templates are in `references/` directory:

| Template File                    | Purpose                                   |
| :------------------------------- | :---------------------------------------- |
| `project-overview-template.md`   | Project facts and stats                   |
| `context-boundaries-template.md` | Module/feature boundaries                 |
| `conventions-template.md`        | Code style and naming rules               |
| `task-recipes-template.md`       | Common commands (build/test/deploy)       |
| `danger-zones-template.md`       | Risk areas and legacy code                |
| `impact-analysis-template.md`    | Dependency relationships                  |
| `database-schema-template.md`    | Database DDL (aggregated from migrations) |
| `critical-flows-template.md`     | Workflows and state machines              |
| `context-index-template.md`      | Root index file (single-file quick ref)   |

## Examples

**Scenario 1: First-time setup**
```
User: "帮我分析这个项目的代码结构"
Agent: Runs analyze_project.py → generates full context suite in {context_dir}
```

**Scenario 2: After major refactor**
```
User: "我重构了 auth 模块，更新一下上下文"
Agent: Updates context-boundaries.md and impact-analysis.md only
```

**Scenario 3: Limit analysis scope**
```bash
# Only analyze Python and JavaScript files
python3 scripts/analyze_project.py . -o .analysis.md --extensions py js

# Shallow scan (3 levels deep)
python3 scripts/analyze_project.py . -o .analysis.md --depth 3
```

## Troubleshooting

| Issue | Solution |
| :---- | :------- |
| `❌ 分析失败` | Check Python version ≥ 3.8; verify project path exists |
| Empty `.analysis.md` | Project may have no recognized code files; use `--extensions` to specify |
| Context files too generic | Quality Gate should prune; if not, manually delete noise files |
| Wrong agent detected | Manually specify `{context_dir}` and `{index_file}` paths |

## Reference

- Templates: `references/` directory relative to this skill file
- Script: [scripts/analyze_project.py](./scripts/analyze_project.py)

**Version**: 1.9.0  
**Last Updated**: 2026-01-21
