---
name: code-context-analyzer
description: Use when asked to analyze project, understand codebase, initialize context, or setting up context for a new codebase
---

# Code Context Analyzer

Generate structured project metadata through static code analysis (AST parsing, dependency graphs, symbol extraction) to help agents understand code and create context files.

**Core Principle**: Treat context creation as a compilation process—compile raw code into structured knowledge artifacts—not just a summarization task.

## Requirements

- Python 3.8+
- 依赖安装：`pip install -r requirements.txt`（tree-sitter 解析器）
- Python 使用标准库 `ast`，其他语言使用 tree-sitter 进行精确语法分析
- Dart/Flutter 暂使用正则解析器作为降级方案

## When NOT to Use

Do NOT use this skill when:
- **Project already has context files** and user just wants to read them (use the existing `.code_analysis/` docs)
- **Quick file lookup** is needed (use file search tools directly)
- **Single file analysis** is requested (read the file directly, skip full project analysis)
- **User mentions specific files/modules** without asking for project-wide understanding
- **Time-critical fixes** where full analysis would delay resolution

## Red Flags - STOP and Re-Evaluate

These signals indicate you're about to violate the protocol:

| Red Flag                                           | What It Means                | Action Required                                        |
| :------------------------------------------------- | :--------------------------- | :----------------------------------------------------- |
| "Let me just generate a summary"                   | Skipping full analysis       | Run `analyze_project.py` first                         |
| "I'll create context files directly"               | Bypassing the analysis phase | Generate `.analysis.md` before any context files       |
| "This is a simple project, I don't need all steps" | Rationalizing shortcuts      | **All projects need the full protocol**                |
| User says "quick analysis"                         | Pressure to skip steps       | Clarify scope; if full context needed, follow protocol |
| "I'll skip the Quality Gate"                       | Accepting low-quality output | **Always** review and prune generic content            |
| Creating files without templates                   | Inconsistent formatting      | Use `references/*.md` templates                        |
| Leaving `.analysis.md` in root                     | Incomplete cleanup           | Delete intermediate files after use                    |

## Context Engineering Protocol

Agent **MUST** follow strictly defined protocols based on the user's intent. Do not skip steps.

### 1. Initialization Protocol

**Trigger**: "Initialize context", "Analyze project", "First time setup"  
**Goal**: Generate the **Full Context Suite**. DO NOT stop after just the overview.
**context_dir**: `.code_analysis/`

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
   .cursor/ → Cursor    |  .windsurf/ → Windsurf  |  .claude/ → ClaudeCode/OpenCode
   .agent/  → Antigravity|  .codex/    → Codex     |  (none)   → Ask user
   ```
   If multiple exist, prefer the one matching current runtime environment.
   
    **Tool-Specific Paths**:

    | Agent                                            | `index_file` (Project Root) |
    | :----------------------------------------------- | :-------------------------- |
    | ClaudeCode                                       | `CLAUDE.md`                 |
    | Others (OpenCode, Cursor, Windsurf, Codex, etc.) | `AGENTS.md`                 |

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

| Change Type                          | Update Target                                   |
| :----------------------------------- | :---------------------------------------------- |
| Structure Change (New files/folders) | `project-overview.md` & `context-boundaries.md` |
| New Dependencies                     | `project-overview.md` & `impact-analysis.md`    |
| Process Change                       | `conventions.md` or `task-recipes.md`           |
| Database Change (New migration/DDL)  | Re-aggregate all SQL → `database-schema.md`     |
| Flow Change (New workflow/state)     | `critical-flows.md` with new flow diagrams      |

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

## Common Mistakes

| Mistake                                        | Why It Happens                                              | How to Fix                                                                          |
| :--------------------------------------------- | :---------------------------------------------------------- | :---------------------------------------------------------------------------------- |
| Generating empty/low-quality context files     | Analysis script failed silently; Quality Gate missed        | Re-run `analyze_project.py`, check Python version, manually delete generic files    |
| Missing `AGENTS.md` or `CLAUDE.md` index       | Skipped Finalize step; forgot to create index from template | Go back to Step 6: Create index file and remove broken links                        |
| Context files mix English and Chinese randomly | Didn't check user's language preference                     | Default to Chinese, but match user's request language if specified                  |
| Leftover `.analysis.md` in project root        | Skipped cleanup step in Finalize                            | Delete intermediate files immediately after use                                     |
| Agent type detection wrong                     | Multiple agent config directories exist                     | Manually specify `{context_dir}` and `{index_file}` paths based on current runtime  |
| Files reference deleted documents in index     | Quality Gate deleted file but index wasn't updated          | Always update index after pruning—remove links to deleted files                     |
| Analysis missing certain file types            | Default extensions don't cover project                      | Use `--extensions` flag to specify additional file types (e.g., `rs`, `go`, `java`) |
| Context outdated after refactor                | Forgot to run Maintenance Protocol                          | Identify change type from table, update only affected documents                     |

## Reference

- Templates: `references/` directory relative to this skill file
- Script: [scripts/analyze_project.py](./scripts/analyze_project.py)
