from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class SymbolInfo:
    """代码符号信息"""
    name: str
    type: str  # 'class', 'function', 'method', 'variable'
    line: int
    end_line: int = 0
    decorators: List[str] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)
    docstring: str = ""


@dataclass
class FileAnalysis:
    """单文件分析结果"""
    path: str
    language: str
    lines: int
    symbols: List[SymbolInfo] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)


@dataclass
class ProjectAnalysis:
    """项目分析结果"""
    name: str
    path: str
    type: str = "Unknown"
    languages: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    package_manager: str = ""
    
    # 统计
    total_files: int = 0
    total_dirs: int = 0
    total_lines: int = 0
    files_by_extension: Dict[str, int] = field(default_factory=dict)
    lines_by_extension: Dict[str, int] = field(default_factory=dict)
    
    # 结构
    directories: List[str] = field(default_factory=list)
    entry_points: List[dict] = field(default_factory=list)
    config_files: List[str] = field(default_factory=list)
    
    # 符号（仅非快速模式）
    files: List[FileAnalysis] = field(default_factory=list)
    
    # 依赖
    external_dependencies: Dict[str, List[dict]] = field(default_factory=dict)
    internal_imports: Dict[str, List[str]] = field(default_factory=dict)
    circular_dependencies: List[List[str]] = field(default_factory=list)
    
    # 元数据
    analyzed_at: str = ""
