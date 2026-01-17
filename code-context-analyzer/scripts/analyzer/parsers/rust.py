import re
from pathlib import Path
from ..core import FileAnalysis, SymbolInfo

class RustAnalyzer:
    """Rust 语言分析器（基于正则）"""
    
    USE_PATTERN = r'^use\s+([^;]+);'
    FN_PATTERN = r'^(?:pub\s+)?(?:async\s+)?fn\s+(\w+)'
    STRUCT_PATTERN = r'^(?:pub\s+)?struct\s+(\w+)'
    ENUM_PATTERN = r'^(?:pub\s+)?enum\s+(\w+)'
    IMPL_PATTERN = r'^impl(?:\s*<[^>]+>)?\s+(\w+)'
    TRAIT_PATTERN = r'^(?:pub\s+)?trait\s+(\w+)'
    
    def analyze(self, file_path: Path) -> FileAnalysis:
        """分析 Rust 文件"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines_list = content.splitlines()
            lines = len(lines_list)
        except UnicodeDecodeError:
            return FileAnalysis(path=str(file_path), language='Rust', lines=0)
        
        symbols = []
        imports = []
        
        for i, line in enumerate(lines_list, 1):
            stripped = line.strip()
            
            # 提取 use 语句
            if match := re.search(self.USE_PATTERN, stripped):
                imports.append(match.group(1).split('::')[0])
            
            # 提取函数
            if match := re.search(self.FN_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='function', line=i))
            
            # 提取结构体
            elif match := re.search(self.STRUCT_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='struct', line=i))
            
            # 提取枚举
            elif match := re.search(self.ENUM_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='enum', line=i))
            
            # 提取 trait
            elif match := re.search(self.TRAIT_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='trait', line=i))
            
            # 提取 impl
            elif match := re.search(self.IMPL_PATTERN, stripped):
                symbols.append(SymbolInfo(name=f"impl {match.group(1)}", type='class', line=i))
        
        return FileAnalysis(
            path=str(file_path),
            language='Rust',
            lines=lines,
            symbols=symbols,
            imports=list(set(imports)),
        )
