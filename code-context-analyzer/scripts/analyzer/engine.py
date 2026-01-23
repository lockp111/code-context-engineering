from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import asdict
from typing import Optional, List, Dict, Set

from .core import ProjectAnalysis, FileAnalysis
from .config import (
    IGNORE_DIRS, IGNORE_PATTERNS, CONFIG_FILES, 
    FRAMEWORK_PATTERNS, CODE_EXTENSIONS, EXTENSION_TO_LANG
)
from .parsers.python import PythonASTAnalyzer
from .parsers.javascript import JSTypeScriptAnalyzer
from .parsers.typescript import TypeScriptAnalyzer
from .parsers.go import GoAnalyzer
from .parsers.rust import RustAnalyzer
from .parsers.cpp import CppAnalyzer
from .parsers.php import PhpAnalyzer
from .parsers.java import JavaAnalyzer
from .parsers.swift import SwiftAnalyzer
from .parsers.kotlin import KotlinAnalyzer
from .parsers.dart import DartAnalyzer
from .parsers.flutter import FlutterAnalyzer

class ProjectAnalyzer:
    """项目分析器"""
    
    def __init__(self, project_path: str, max_depth: int = 4, extensions: Optional[List[str]] = None):
        self.project_path = Path(project_path).resolve()
        self.max_depth = max_depth
        self.extensions = set(f".{e.lstrip('.')}" for e in extensions) if extensions else None
        
        # 分析器
        self.python_analyzer = PythonASTAnalyzer()
        self.js_analyzer = JSTypeScriptAnalyzer()
        self.ts_analyzer = TypeScriptAnalyzer()
        self.go_analyzer = GoAnalyzer()
        self.rust_analyzer = RustAnalyzer()
        self.cpp_analyzer = CppAnalyzer()
        self.php_analyzer = PhpAnalyzer()
        self.java_analyzer = JavaAnalyzer()
        self.swift_analyzer = SwiftAnalyzer()
        self.kotlin_analyzer = KotlinAnalyzer()
        self.dart_analyzer = DartAnalyzer()
        self.flutter_analyzer = FlutterAnalyzer()
        
        # Flutter 项目检测
        self._is_flutter_project = self._detect_flutter_project()
        
        # 结果
        self.result = ProjectAnalysis(
            name=self.project_path.name,
            path=str(self.project_path),
            analyzed_at=datetime.now().isoformat(),
        )
    
    def analyze(self) -> ProjectAnalysis:
        """执行完整分析"""
        print(f"📂 分析项目: {self.project_path}", file=sys.stderr)
        
        # Phase 1: 扫描结构
        print("  → 扫描目录结构...", file=sys.stderr)
        self._scan_structure()
        
        # Phase 2: 检测项目类型
        print("  → 检测项目类型...", file=sys.stderr)
        self._detect_project_type()
        
        # Phase 3: 分析依赖
        print("  → 分析依赖...", file=sys.stderr)
        self._analyze_dependencies()
        
        # Phase 4: 识别入口点
        print("  → 识别入口点...", file=sys.stderr)
        self._find_entry_points()
        
        # Phase 5: AST 分析（总是执行）
        print("  → 分析代码符号...", file=sys.stderr)
        self._analyze_symbols()
        
        print("  → 分析内部依赖...", file=sys.stderr)
        self._analyze_internal_imports()
        
        print("  → 检测循环依赖...", file=sys.stderr)
        self._detect_circular_dependencies()
        
        print("✅ 分析完成!", file=sys.stderr)
        return self.result
    
    def _detect_flutter_project(self) -> bool:
        """检测是否为 Flutter 项目"""
        pubspec = self.project_path / 'pubspec.yaml'
        if pubspec.exists():
            try:
                content = pubspec.read_text(encoding='utf-8')
                # 检查是否有 Flutter SDK 依赖
                if 'flutter:' in content and 'sdk: flutter' in content:
                    return True
            except Exception:
                pass
        return False
    
    def _scan_structure(self, path: Optional[Path] = None, depth: int = 0):
        """递归扫描目录结构"""
        if path is None:
            path = self.project_path
        
        if depth > self.max_depth:
            return
        
        try:
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            return
        
        for item in items:
            if item.is_dir():
                if item.name in IGNORE_DIRS or item.name.startswith('.'):
                    continue
                self.result.total_dirs += 1
                rel_path = str(item.relative_to(self.project_path))
                self.result.directories.append(rel_path)
                self._scan_structure(item, depth + 1)
            else:
                # 跳过忽略的文件
                if any(item.match(p) for p in IGNORE_PATTERNS):
                    continue
                if item.name.startswith('.') and item.suffix not in ['.env', '.gitignore']:
                    continue
                
                ext = item.suffix.lower() or '.no_extension'
                
                # 如果指定了扩展名过滤
                if self.extensions and ext not in self.extensions:
                    continue
                
                self.result.total_files += 1
                self.result.files_by_extension[ext] = self.result.files_by_extension.get(ext, 0) + 1
                
                # 计算行数（仅对代码文件）
                if ext in CODE_EXTENSIONS and self.result.total_files <= 1000:
                    try:
                        lines = len(item.read_text(encoding='utf-8', errors='ignore').splitlines())
                        self.result.total_lines += lines
                        self.result.lines_by_extension[ext] = self.result.lines_by_extension.get(ext, 0) + lines
                    except Exception:
                        pass
    
    def _detect_project_type(self):
        """检测项目类型和技术栈"""
        for config_file, project_type in CONFIG_FILES.items():
            config_path = self.project_path / config_file
            if config_path.exists():
                self.result.config_files.append(config_file)
                if self.result.type == "Unknown":
                    self.result.type = project_type
        
        # 根据文件扩展名推断语言
        for ext, count in sorted(self.result.files_by_extension.items(), key=lambda x: x[1], reverse=True):
            if ext in EXTENSION_TO_LANG and count > 0:
                lang = EXTENSION_TO_LANG[ext]
                if lang not in self.result.languages:
                    self.result.languages.append(lang)
    
    def _analyze_dependencies(self):
        """分析项目依赖"""
        # Node.js 项目
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text(encoding='utf-8'))
                self.result.name = data.get('name', self.result.name)
                self.result.package_manager = 'npm/yarn'
                
                # 生产依赖
                prod_deps = []
                for dep, version in data.get('dependencies', {}).items():
                    prod_deps.append({'name': dep, 'version': version})
                    # 检测框架
                    for framework, patterns in FRAMEWORK_PATTERNS.items():
                        if dep in patterns and framework not in self.result.frameworks:
                            self.result.frameworks.append(framework)
                
                # 开发依赖
                dev_deps = []
                for dep, version in data.get('devDependencies', {}).items():
                    dev_deps.append({'name': dep, 'version': version})
                
                self.result.external_dependencies = {
                    'production': prod_deps,
                    'development': dev_deps,
                }
            except Exception:
                pass
        
        # Python 项目
        requirements = self.project_path / 'requirements.txt'
        if requirements.exists():
            try:
                self.result.package_manager = 'pip'
                deps = []
                for line in requirements.read_text(encoding='utf-8').splitlines():
                    line = line.strip()
                    if line and not line.startswith('#'):
                        match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                        if match:
                            deps.append({'name': match.group(1), 'version': line})
                self.result.external_dependencies = {'production': deps}
            except Exception:
                pass
        
        pyproject = self.project_path / 'pyproject.toml'
        if pyproject.exists():
            self.result.package_manager = 'poetry/pip'
    
    def _find_entry_points(self):
        """识别入口点"""
        common_entry_points = [
            ('src/index.ts', 'Main entry (TypeScript)'),
            ('src/index.js', 'Main entry (JavaScript)'),
            ('src/main.ts', 'Main entry (TypeScript)'),
            ('src/main.js', 'Main entry (JavaScript)'),
            ('index.ts', 'Root entry (TypeScript)'),
            ('index.js', 'Root entry (JavaScript)'),
            ('main.py', 'Main entry (Python)'),
            ('app.py', 'App entry (Python)'),
            ('src/main.py', 'Main entry (Python)'),
            ('src/app.py', 'App entry (Python)'),
            ('cmd/main.go', 'Main entry (Go)'),
            ('main.go', 'Main entry (Go)'),
            ('src/main.rs', 'Main entry (Rust)'),
            ('src/lib.rs', 'Library entry (Rust)'),
        ]
        
        for entry_path, description in common_entry_points:
            if (self.project_path / entry_path).exists():
                self.result.entry_points.append({
                    'path': entry_path,
                    'description': description,
                })
        
        # 从 package.json 获取入口点
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text(encoding='utf-8'))
                if 'main' in data:
                    self.result.entry_points.append({
                        'path': data['main'],
                        'description': 'Package main',
                    })
                if 'bin' in data:
                    if isinstance(data['bin'], str):
                        self.result.entry_points.append({
                            'path': data['bin'],
                            'description': 'CLI binary',
                        })
                    elif isinstance(data['bin'], dict):
                        for name, path in data['bin'].items():
                            self.result.entry_points.append({
                                'path': path,
                                'description': f'CLI: {name}',
                            })
            except Exception:
                pass
    
    def _analyze_symbols(self):
        """分析代码符号（AST 分析）"""
        src_dirs = ['src', 'lib', 'app', 'pkg', 'internal', '.']
        analyzed_count = 0
        max_files = 200  # 限制分析文件数量
        
        for src_dir in src_dirs:
            src_path = self.project_path / src_dir if src_dir != '.' else self.project_path
            if not src_path.exists():
                continue
            
            for file_path in src_path.rglob('*'):
                if analyzed_count >= max_files:
                    break
                
                if not file_path.is_file():
                    continue
                
                # 跳过忽略的目录
                if any(part in IGNORE_DIRS for part in file_path.parts):
                    continue
                
                ext = file_path.suffix.lower()
                
                analysis = None
                
                if ext == '.py':
                    analysis = self.python_analyzer.analyze(file_path)
                elif ext in ['.js', '.jsx']:
                    analysis = self.js_analyzer.analyze(file_path)
                elif ext in ['.ts', '.tsx']:
                    analysis = self.ts_analyzer.analyze(file_path)
                elif ext == '.go':
                    analysis = self.go_analyzer.analyze(file_path)
                elif ext == '.rs':
                    analysis = self.rust_analyzer.analyze(file_path)
                elif ext in ['.c', '.cpp', '.h', '.hpp', '.cc', '.cxx', '.hxx', '.hh']:
                    analysis = self.cpp_analyzer.analyze(file_path)
                elif ext == '.php':
                    analysis = self.php_analyzer.analyze(file_path)
                elif ext == '.java':
                    analysis = self.java_analyzer.analyze(file_path)
                elif ext == '.swift':
                    analysis = self.swift_analyzer.analyze(file_path)
                elif ext == '.kt':
                    analysis = self.kotlin_analyzer.analyze(file_path)
                elif ext == '.dart':
                    # 如果是 Flutter 项目，使用 Flutter 解析器
                    if self._is_flutter_project:
                        analysis = self.flutter_analyzer.analyze(file_path)
                    else:
                        analysis = self.dart_analyzer.analyze(file_path)

                if analysis and (analysis.symbols or analysis.imports):
                    # 确保 path 字段是相对路径
                    analysis.path = str(file_path.relative_to(self.project_path))
                    self.result.files.append(analysis)
                    analyzed_count += 1
    
    def _analyze_internal_imports(self):
        """分析内部导入关系"""
        for file_analysis in self.result.files:
            internal_imports = []
            for imp in file_analysis.imports:
                # 判断是否是内部导入
                if imp.startswith('.') or imp.startswith(self.result.name):
                    internal_imports.append(imp)
                # 检查是否可能是项目内的模块
                elif not imp.startswith('@') and '/' not in imp:
                    # 可能是相对导入或项目模块
                    potential_paths = [
                        self.project_path / f"{imp}.py",
                        self.project_path / imp / "__init__.py",
                        self.project_path / "src" / f"{imp}.py",
                        self.project_path / "src" / imp / "__init__.py",
                    ]
                    if any(p.exists() for p in potential_paths):
                        internal_imports.append(imp)
            
            if internal_imports:
                self.result.internal_imports[file_analysis.path] = internal_imports
    
    def _detect_circular_dependencies(self):
        """检测循环依赖（使用 DFS）"""
        # 构建导入图：文件路径 -> 导入的模块名
        graph = self.result.internal_imports
        
        if not graph:
            return
        
        # 创建模块名到文件路径的映射
        module_to_file: Dict[str, str] = {}
        for file_path in graph:
            # 从文件路径提取可能的模块名
            path = Path(file_path)
            # Python: foo/bar.py -> foo.bar 或 bar
            if path.suffix == '.py':
                module_name = path.stem
                if module_name != '__init__':
                    module_to_file[module_name] = file_path
                # 也用目录名
                if len(path.parts) > 1:
                    dir_module = path.parts[-2]
                    module_to_file[dir_module] = file_path
            else:
                # JS/TS/Go/Rust: 用文件名（无扩展）
                module_to_file[path.stem] = file_path
        
        # 标准化图：文件路径 -> 文件路径列表
        normalized_graph: Dict[str, List[str]] = {}
        for file_path, imports in graph.items():
            deps = []
            for imp in imports:
                # 尝试解析模块名到文件路径
                imp_name = imp.lstrip('.').split('/')[-1].split('.')[-1]
                if imp_name in module_to_file:
                    deps.append(module_to_file[imp_name])
            if deps:
                normalized_graph[file_path] = deps
        
        # DFS 检测循环
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycles: List[List[str]] = []
        
        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in normalized_graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    # 找到循环
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    # 避免重复（规范化循环表示）
                    normalized = tuple(sorted(cycle[:-1]))
                    if normalized not in [tuple(sorted(c[:-1])) for c in cycles]:
                        cycles.append(cycle)
            
            path.pop()
            rec_stack.remove(node)
        
        for node in normalized_graph:
            if node not in visited:
                dfs(node, [])
        
        self.result.circular_dependencies = cycles
    
    def to_dict(self) -> dict:
        """转换为字典"""
        def convert(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return {k: convert(v) for k, v in asdict(obj).items()}
            elif isinstance(obj, list):
                return [convert(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            return obj
        
        return convert(self.result)
