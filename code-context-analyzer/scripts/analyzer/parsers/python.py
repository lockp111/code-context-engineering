import ast
from pathlib import Path
from ..core import FileAnalysis, SymbolInfo


class PythonASTAnalyzer:
    """Python AST 分析器 — 使用 NodeVisitor 正确区分顶层函数和类方法"""

    def analyze(self, file_path: Path) -> FileAnalysis:
        """分析 Python 文件"""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = len(content.splitlines())
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError):
            return FileAnalysis(
                path=str(file_path),
                language="Python",
                lines=0,
            )

        visitor = _SymbolVisitor()
        visitor.visit(tree)

        return FileAnalysis(
            path=str(file_path),
            language="Python",
            lines=lines,
            symbols=visitor.symbols,
            imports=list(set(visitor.imports)),
        )


class _SymbolVisitor(ast.NodeVisitor):
    """AST visitor that tracks parent context to distinguish functions from methods."""

    def __init__(self):
        self.symbols: list[SymbolInfo] = []
        self.imports: list[str] = []
        self._class_depth = 0  # Track nesting inside class definitions

    # ── Imports ──────────────────────────────────────────────────────────

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)

    # ── Classes ──────────────────────────────────────────────────────────

    def visit_ClassDef(self, node: ast.ClassDef):
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        docstring = ast.get_docstring(node) or ""
        self.symbols.append(
            SymbolInfo(
                name=node.name,
                type="class",
                line=node.lineno,
                end_line=node.end_lineno or node.lineno,
                decorators=decorators,
                docstring=docstring[:200] if docstring else "",
            )
        )
        # Recurse into class body with incremented depth
        self._class_depth += 1
        self.generic_visit(node)
        self._class_depth -= 1

    # ── Functions / Methods ──────────────────────────────────────────────

    def _visit_function(self, node):
        """Handle both FunctionDef and AsyncFunctionDef."""
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        params = [arg.arg for arg in node.args.args if arg.arg != "self"]
        docstring = ast.get_docstring(node) or ""

        # Key fix: use _class_depth to distinguish method from function
        sym_type = "method" if self._class_depth > 0 else "function"

        self.symbols.append(
            SymbolInfo(
                name=node.name,
                type=sym_type,
                line=node.lineno,
                end_line=node.end_lineno or node.lineno,
                decorators=decorators,
                parameters=params[:10],
                docstring=docstring[:200] if docstring else "",
            )
        )
        # Do NOT recurse into nested functions by default
        # (we only want top-level and class-level symbols)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._visit_function(node)

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _get_decorator_name(decorator) -> str:
        """提取装饰器名称"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Call):
            return _SymbolVisitor._get_decorator_name(decorator.func)
        return ""
