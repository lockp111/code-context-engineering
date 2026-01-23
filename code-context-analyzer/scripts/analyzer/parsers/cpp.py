import re
from pathlib import Path
from ..core import FileAnalysis, SymbolInfo

class CppAnalyzer:
    """C/C++ 语言分析器（基于正则）"""
    
    INCLUDE_PATTERN = r'^\s*#include\s+["<]([^">]+)[">]'
    CLASS_PATTERN = r'^\s*(?:template\s*<[^>]*>\s*)?(?:class|struct)\s+(\w+)'
    # 简化的函数匹配：返回类型 函数名(参数)
    # 排除 if/while/for 等关键字
    FUNCTION_PATTERN = r'^\s*(?!if|while|for|switch|return|else)(?:[\w:<>*&]+\s+)+(\w+)\s*\('
    # 枚举定义
    ENUM_PATTERN = r'^\s*enum\s+(?:class\s+)?(\w+)'
    # typedef 和 using 类型别名
    TYPEDEF_PATTERN = r'^\s*typedef\s+.*\s+(\w+)\s*;'
    USING_PATTERN = r'^\s*using\s+(\w+)\s*='
    # namespace 定义
    NAMESPACE_PATTERN = r'^\s*namespace\s+(\w+)'
    
    def analyze(self, file_path: Path) -> FileAnalysis:
        """分析 C/C++ 文件"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines_list = content.splitlines()
            lines = len(lines_list)
        except UnicodeDecodeError:
            return FileAnalysis(path=str(file_path), language='C++', lines=0)
        
        symbols = []
        imports = []
        
        ext = file_path.suffix.lower()
        # 兼容更多扩展名
        lang = 'C' if ext in ['.c', '.h'] else 'C++'
        
        for i, line in enumerate(lines_list, 1):
            stripped = line.strip()
            
            # 提取 include
            if match := re.search(self.INCLUDE_PATTERN, stripped):
                imports.append(match.group(1))
                continue
            
            # 提取类/结构体
            if match := re.search(self.CLASS_PATTERN, stripped):
                matched_text = match.group(0)
                is_struct = 'struct' in matched_text
                symbols.append(SymbolInfo(name=match.group(1), type='struct' if is_struct else 'class', line=i))
            
            # 提取枚举
            elif match := re.search(self.ENUM_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='enum', line=i))
            
            # 提取 namespace
            elif match := re.search(self.NAMESPACE_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='namespace', line=i))
            
            # 提取 typedef
            elif match := re.search(self.TYPEDEF_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='type', line=i))
            
            # 提取 using 别名
            elif match := re.search(self.USING_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='type', line=i))
            
            # 提取函数
            elif match := re.search(self.FUNCTION_PATTERN, stripped):
                func_name = match.group(1)
                # 过滤关键字误判
                if func_name not in ['main', 'if', 'while', 'for', 'switch']:
                    symbols.append(SymbolInfo(name=func_name, type='function', line=i))
        
        return FileAnalysis(
            path=str(file_path),
            language=lang,
            lines=lines,
            symbols=symbols,
            imports=list(set(imports)),
        )
