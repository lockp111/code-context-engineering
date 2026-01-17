import re
from pathlib import Path
from ..core import FileAnalysis, SymbolInfo

class PhpAnalyzer:
    """PHP 语言分析器（基于正则）"""
    
    USE_PATTERN = r'^\s*use\s+([^;]+);'
    CLASS_PATTERN = r'^\s*(?:abstract\s+|final\s+)?class\s+(\w+)'
    INTERFACE_PATTERN = r'^\s*interface\s+(\w+)'
    TRAIT_PATTERN = r'^\s*trait\s+(\w+)'
    FUNCTION_PATTERN = r'^\s*(?:public|protected|private|static|abstract|\s)*function\s+&?(\w+)\s*\('
    
    def analyze(self, file_path: Path) -> FileAnalysis:
        """分析 PHP 文件"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines_list = content.splitlines()
            lines = len(lines_list)
        except UnicodeDecodeError:
            return FileAnalysis(path=str(file_path), language='PHP', lines=0)
        
        symbols = []
        imports = []
        
        for i, line in enumerate(lines_list, 1):
            stripped = line.strip()
            
            # Use 语句
            if match := re.search(self.USE_PATTERN, stripped):
                imports.append(match.group(1))
            
            # Class
            elif match := re.search(self.CLASS_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='class', line=i))
            
            # Interface
            elif match := re.search(self.INTERFACE_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='interface', line=i))
            
            # Trait
            elif match := re.search(self.TRAIT_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='trait', line=i))
            
            # Function
            elif match := re.search(self.FUNCTION_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='function', line=i))
                
        return FileAnalysis(
            path=str(file_path),
            language='PHP',
            lines=lines,
            symbols=symbols,
            imports=list(set(imports)),
        )
