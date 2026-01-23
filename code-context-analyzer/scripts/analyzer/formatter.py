from __future__ import annotations

from typing import List
from .core import ProjectAnalysis, FileAnalysis, SymbolInfo

def to_markdown(analysis: ProjectAnalysis) -> str:
    """
    Generate a high-density Markdown representation of the project analysis.
    Optimized for LLM context window efficiency.
    """
    lines = []
    
    # 1. Header & Stats
    lines.append(f"# Project: {analysis.name}")
    lines.append(f"Root: {analysis.path}")
    lines.append(f"Type: {analysis.type} | PackageManager: {analysis.package_manager or 'N/A'}")
    lines.append(f"Stats: {analysis.total_files} files, {analysis.total_lines} lines, {analysis.total_dirs} directories")
    
    if analysis.languages:
        lines.append(f"Languages: {', '.join(analysis.languages)}")
    if analysis.frameworks:
        lines.append(f"Frameworks: {', '.join(analysis.frameworks)}")
    
    lines.append("")
    
    # 2. Key Directories (Structure)
    # We only show top 2 levels or just the list provided by analysis
    if analysis.directories:
        lines.append("## Directory Structure")
        # Sort directories for consistent output
        sorted_dirs = sorted(analysis.directories)
        # Simple tree-like view is hard with just a list of paths, so we just list them nicely
        # Or just listing them is fine for "dense" context.
        # Let's try to group them if possible, but for now linear list is safest.
        for d in sorted_dirs:
            lines.append(f"- {d}/")
        lines.append("")

    # 3. Dependencies
    if analysis.external_dependencies:
        lines.append("## Dependencies")
        for category, deps in analysis.external_dependencies.items():
            if deps:
                lines.append(f"### {category.title()}")
                # Compact list: name (version), name (version)
                dep_strs = []
                for dep in deps:
                    ver = f" ({dep['version']})" if dep.get('version') else ""
                    dep_strs.append(f"{dep['name']}{ver}")
                lines.append(", ".join(dep_strs))
        lines.append("")

    # 4. Entry Points
    if analysis.entry_points:
        lines.append("## Entry Points")
        for ep in analysis.entry_points:
            lines.append(f"- {ep['path']}: {ep['description']}")
        lines.append("")
    
    # 5. Core Logic (Symbols) - The Meat
    if analysis.files:
        lines.append("## Code Symbols")
        
        # Sort files by path
        sorted_files = sorted(analysis.files, key=lambda f: f.path)
        
        for f in sorted_files:
            # File Header: Path (Language, Lines)
            lines.append(f"### {f.path} ({f.language})")
            
            # Imports (Optional: might be too noisy, lets include them on one line)
            # if f.imports:
            #    lines.append(f"  Imports: {', '.join(f.imports[:10])}{'...' if len(f.imports)>10 else ''}")
            
            # Symbols
            if f.symbols:
                for sym in f.symbols:
                    _format_symbol(sym, lines)
            else:
                lines.append("  (No symbols found)")
            
            lines.append("")

    return "\n".join(lines)

def _format_symbol(sym: SymbolInfo, output_lines: List[str]):
    """Helper to format a single symbol compactly."""
    # Prefix based on type
    prefix_map = {
        'class': 'C',
        'function': 'F',
        'method': 'M',
        'variable': 'V',
        'interface': 'I',
        'trait': 'T',
    }
    # Fallback to first char upper or '?'
    prefix = prefix_map.get(sym.type, sym.type[0].upper() if sym.type else '?')
    
    # Parameters
    params_str = ""
    if sym.parameters:
        params_str = f"({', '.join(sym.parameters)})"
    elif sym.type in ['function', 'method']:
        params_str = "()"
        
    # Decorators
    dec_str = ""
    if sym.decorators:
        dec_str = f" @{', @'.join(sym.decorators)}"
        
    # Line
    line_info = f" L{sym.line}"
    
    # Construct line: "- [C] ClassName L10"
    output_lines.append(f"- [{prefix}] {sym.name}{params_str}{dec_str}{line_info}")
