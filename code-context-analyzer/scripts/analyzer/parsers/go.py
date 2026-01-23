import re
from pathlib import Path
from ..core import FileAnalysis, SymbolInfo

class GoAnalyzer:
    """Go 语言分析器（基于正则）"""
    
    IMPORT_PATTERN = r'import\s+(?:\(\s*([\s\S]*?)\s*\)|"([^"]+)")'
    # 宽松的正则：允许函数名后跟泛型 [T any] 等，不再强制匹配 (
    FUNC_PATTERN = r'^func\s+(?:\([^)]+\)\s+)?(\w+)'
    # 宽松的正则：允许结构体名后跟泛型
    STRUCT_PATTERN = r'^type\s+(\w+).*\s+struct\s*\{'
    # 宽松的正则：允许接口名后跟泛型
    INTERFACE_PATTERN = r'^type\s+(\w+).*\s+interface\s*\{'
    # 类型别名：type Alias int 或 type Alias = int (Go 1.9+)
    TYPE_ALIAS_PATTERN = r'^type\s+(\w+)\s+=?\s*(\w+|\[|func|chan|map)'
    # 常量定义
    CONST_PATTERN = r'^(?:const|var)\s+(\w+)\s+'
    
    def analyze(self, file_path: Path) -> FileAnalysis:
        """分析 Go 文件"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines_list = content.splitlines()
            lines = len(lines_list)
        except UnicodeDecodeError:
            return FileAnalysis(path=str(file_path), language='Go', lines=0)
        
        symbols = []
        imports = []
        
        # 提取导入
        for match in re.finditer(self.IMPORT_PATTERN, content):
            if match.group(1):  # 多行导入
                for line in match.group(1).splitlines():
                    line = line.strip().strip('"')
                    if line and not line.startswith('//'):
                        imports.append(line.split()[-1].strip('"'))
            elif match.group(2):  # 单行导入
                imports.append(match.group(2))
        
        # 提取符号
        for i, line in enumerate(lines_list, 1):
            if match := re.search(self.FUNC_PATTERN, line):
                symbols.append(SymbolInfo(name=match.group(1), type='function', line=i))
            elif match := re.search(self.STRUCT_PATTERN, line):
                symbols.append(SymbolInfo(name=match.group(1), type='struct', line=i))
            elif match := re.search(self.INTERFACE_PATTERN, line):
                symbols.append(SymbolInfo(name=match.group(1), type='interface', line=i))
            elif match := re.search(self.TYPE_ALIAS_PATTERN, line):
                symbols.append(SymbolInfo(name=match.group(1), type='type', line=i))
            elif match := re.search(self.CONST_PATTERN, line):
                symbols.append(SymbolInfo(name=match.group(1), type='const', line=i))
        
        return FileAnalysis(
            path=str(file_path),
            language='Go',
            lines=lines,
            symbols=symbols,
            imports=list(set(imports)),
        )
