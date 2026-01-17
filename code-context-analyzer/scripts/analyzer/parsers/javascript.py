import re
from pathlib import Path
from ..core import FileAnalysis, SymbolInfo

class JSTypeScriptAnalyzer:
    """JavaScript/TypeScript 分析器（基于正则）"""
    
    # 正则模式
    IMPORT_PATTERNS = [
        r"import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]",
        r"import\s+['\"]([^'\"]+)['\"]",
        r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
    ]
    
    EXPORT_PATTERNS = [
        r"export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)",
        r"export\s*\{\s*([^}]+)\s*\}",
        r"module\.exports\s*=",
    ]
    
    CLASS_PATTERN = r"(?:export\s+)?(?:default\s+)?class\s+(\w+)"
    FUNCTION_PATTERN = r"(?:export\s+)?(?:async\s+)?function\s+(\w+)"
    ARROW_FUNCTION_PATTERN = r"(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>"
    METHOD_PATTERN = r"^\s*(?:(?:public|protected|private|static|abstract|async)\s+)*(\w+)\s*\("
    
    def analyze(self, file_path: Path) -> FileAnalysis:
        """分析 JS/TS 文件"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines_list = content.splitlines()
            lines = len(lines_list)
        except UnicodeDecodeError:
            return FileAnalysis(
                path=str(file_path),
                language='JavaScript',
                lines=0,
            )
        
        ext = file_path.suffix.lower()
        language = 'TypeScript' if ext in ['.ts', '.tsx'] else 'JavaScript'
        
        symbols = []
        imports = []
        exports = []
        
        # 提取导入
        for pattern in self.IMPORT_PATTERNS:
            for match in re.finditer(pattern, content):
                imports.append(match.group(1))
        
        # 提取导出
        for pattern in self.EXPORT_PATTERNS:
            for match in re.finditer(pattern, content):
                if match.lastindex:
                    exports.append(match.group(1))
        
        # 提取定义
        excluded_keywords = {'if', 'for', 'while', 'switch', 'catch', 'super'}
        
        for i, line in enumerate(lines_list, 1):
            stripped = line.strip()
            
            # 提取类
            if match := re.search(self.CLASS_PATTERN, line):
                symbols.append(SymbolInfo(
                    name=match.group(1),
                    type='class',
                    line=i,
                ))
            
            # 提取函数
            elif match := re.search(self.FUNCTION_PATTERN, line):
                symbols.append(SymbolInfo(
                    name=match.group(1),
                    type='function',
                    line=i,
                ))
            
            # 提取箭头函数
            elif match := re.search(self.ARROW_FUNCTION_PATTERN, line):
                symbols.append(SymbolInfo(
                    name=match.group(1),
                    type='function',
                    line=i,
                ))
                
            # 提取类方法 (排除关键字)
            elif match := re.search(self.METHOD_PATTERN, stripped):
                name = match.group(1)
                if name not in excluded_keywords:
                    # 避免重复：如果是 function 定义已经被上面捕获
                    # METHOD_PATTERN 匹配 `name(`，`function name(` 也会匹配到 `function`?
                    # `METHOD_PATTERN` starts with `^\s*`.
                    # `function name()`: `function` is captured as name? No.
                    # `function name()` -> `function` matches `(\w+)`. `name` matches `\s*\(`.
                    # No, `function name()`: `function` followed by space. `\(` expects paren.
                    # So `function name` does not match `name(`. 
                    # `function` keyword is safe? `function (` ? Anonymous function. `function` matches `(\w+)`. `(` matches `\(`.
                    # So anonymous function `function()` matches name `function`.
                    # We should exclude `function` from method names.
                    if name != 'function':
                        symbols.append(SymbolInfo(
                            name=name,
                            type='function', # Method treated as function
                            line=i,
                        ))
        
        return FileAnalysis(
            path=str(file_path),
            language=language,
            lines=lines,
            symbols=symbols,
            imports=list(set(imports)),
            exports=exports,
        )
