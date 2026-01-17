import ast
from pathlib import Path
from ..core import FileAnalysis, SymbolInfo

class PythonASTAnalyzer:
    """Python AST 分析器"""
    
    def analyze(self, file_path: Path) -> FileAnalysis:
        """分析 Python 文件"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = len(content.splitlines())
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError):
            return FileAnalysis(
                path=str(file_path),
                language='Python',
                lines=0,
            )
        
        symbols = []
        imports = []
        
        for node in ast.walk(tree):
            # 导入
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
            
            # 类
            elif isinstance(node, ast.ClassDef):
                decorators = [self._get_decorator_name(d) for d in node.decorator_list]
                docstring = ast.get_docstring(node) or ""
                symbols.append(SymbolInfo(
                    name=node.name,
                    type='class',
                    line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    decorators=decorators,
                    docstring=docstring[:200] if docstring else "",
                ))
            
            # 顶层函数
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # 检查是否是顶层函数（不在类内）
                decorators = [self._get_decorator_name(d) for d in node.decorator_list]
                params = [arg.arg for arg in node.args.args if arg.arg != 'self']
                docstring = ast.get_docstring(node) or ""
                symbols.append(SymbolInfo(
                    name=node.name,
                    type='function',
                    line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    decorators=decorators,
                    parameters=params[:10],  # 限制参数数量
                    docstring=docstring[:200] if docstring else "",
                ))
        
        return FileAnalysis(
            path=str(file_path),
            language='Python',
            lines=lines,
            symbols=symbols,
            imports=list(set(imports)),
        )
    
    def _get_decorator_name(self, decorator) -> str:
        """提取装饰器名称"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Call):
            return self._get_decorator_name(decorator.func)
        return ""
