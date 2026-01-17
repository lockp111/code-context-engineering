import re
from pathlib import Path
from ..core import FileAnalysis, SymbolInfo
from .javascript import JSTypeScriptAnalyzer

class TypeScriptAnalyzer(JSTypeScriptAnalyzer):
    """TypeScript 分析器（基于正则）"""
    
    # 新增 TS 特有模式
    INTERFACE_PATTERN = r"(?:export\s+)?interface\s+(\w+)"
    TYPE_PATTERN = r"(?:export\s+)?type\s+(\w+)\s*="
    ENUM_PATTERN = r"(?:export\s+)?(?:const\s+)?enum\s+(\w+)"
    
    def analyze(self, file_path: Path) -> FileAnalysis:
        """分析 TS/TSX 文件"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines_list = content.splitlines()
            lines = len(lines_list)
        except UnicodeDecodeError:
            return FileAnalysis(
                path=str(file_path),
                language='TypeScript',
                lines=0,
            )
        
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
        
        # 逐行分析定义
        excluded_keywords = {'if', 'for', 'while', 'switch', 'catch', 'super'}

        for i, line in enumerate(lines_list, 1):
            stripped = line.strip()

            # 1. 复用 JS 的模式
            # Class
            if match := re.search(self.CLASS_PATTERN, line):
                symbols.append(SymbolInfo(name=match.group(1), type='class', line=i))
            # Function
            elif match := re.search(self.FUNCTION_PATTERN, line):
                symbols.append(SymbolInfo(name=match.group(1), type='function', line=i))
            # Arrow Function
            elif match := re.search(self.ARROW_FUNCTION_PATTERN, line):
                symbols.append(SymbolInfo(name=match.group(1), type='function', line=i))
            
            # 2. TS 特有模式
            # Interface
            elif match := re.search(self.INTERFACE_PATTERN, line):
                symbols.append(SymbolInfo(name=match.group(1), type='interface', line=i))
            # Type Alias
            elif match := re.search(self.TYPE_PATTERN, line):
                symbols.append(SymbolInfo(name=match.group(1), type='type', line=i))
            # Enum
            elif match := re.search(self.ENUM_PATTERN, line):
                symbols.append(SymbolInfo(name=match.group(1), type='enum', line=i))
            
            # 3. 类方法 (排除关键字)
            # Use stripped line for anchors in METHOD_PATTERN
            elif match := re.search(self.METHOD_PATTERN, stripped):
                name = match.group(1)
                if name not in excluded_keywords and name != 'function':
                    symbols.append(SymbolInfo(name=name, type='function', line=i))
        
        return FileAnalysis(
            path=str(file_path),
            language='TypeScript',
            lines=lines,
            symbols=symbols,
            imports=list(set(imports)),
            exports=exports,
        )
