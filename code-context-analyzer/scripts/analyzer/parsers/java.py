import re
from pathlib import Path
from ..core import FileAnalysis, SymbolInfo

class JavaAnalyzer:
    """Java 语言分析器（基于正则）"""
    
    # 通用修饰符（顺序无关）
    MODIFIERS = r'(?:(?:public|private|protected|static|final|abstract|synchronized|native|strictfp|default|sealed|non-sealed|transient|volatile)\s+)*'
    
    # 导入
    IMPORT_PATTERN = r'^\s*import\s+(?:static\s+)?([^;]+);'
    PACKAGE_PATTERN = r'^\s*package\s+([^;]+);'
    
    # 类/接口/枚举（修饰符顺序无关）
    CLASS_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)'
    INTERFACE_PATTERN = rf'^\s*{MODIFIERS}interface\s+(\w+)'
    ENUM_PATTERN = rf'^\s*{MODIFIERS}enum\s+(\w+)'
    RECORD_PATTERN = rf'^\s*{MODIFIERS}record\s+(\w+)'
    ANNOTATION_PATTERN = rf'^\s*{MODIFIERS}@interface\s+(\w+)'
    
    # 方法（支持泛型返回类型）
    METHOD_PATTERN = rf'^\s*(?:@\w+\s+)*{MODIFIERS}(?:<[^>]+>\s+)?[\w<>\[\],\.\s]+\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*[{{;]'
    
    # 常量（public static final）
    CONSTANT_PATTERN = rf'^\s*{MODIFIERS}[\w<>\[\]]+\s+([A-Z][A-Z0-9_]*)\s*='
    
    def analyze(self, file_path: Path) -> FileAnalysis:
        """分析 Java 文件"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines_list = content.splitlines()
            lines = len(lines_list)
        except UnicodeDecodeError:
            return FileAnalysis(path=str(file_path), language='Java', lines=0)
        
        symbols = []
        imports = []
        class_names = set()  # 跟踪类名，用于排除构造函数
        in_multiline_comment = False
        
        # 排除的方法名（关键字）
        excluded = {'if', 'for', 'while', 'switch', 'catch', 'synchronized', 'return', 'throw', 'new', 'try', 'else'}
        
        for i, line in enumerate(lines_list, 1):
            # 处理多行注释
            line_to_parse = line
            
            # 处理多行注释状态
            if in_multiline_comment:
                if '*/' in line_to_parse:
                    # 注释结束，保留 */ 之后的内容
                    line_to_parse = line_to_parse[line_to_parse.index('*/') + 2:]
                    in_multiline_comment = False
                else:
                    continue
            
            # 移除行内 /* */ 注释
            while '/*' in line_to_parse:
                start = line_to_parse.index('/*')
                if '*/' in line_to_parse[start:]:
                    end = line_to_parse.index('*/', start) + 2
                    line_to_parse = line_to_parse[:start] + line_to_parse[end:]
                else:
                    # 多行注释开始
                    line_to_parse = line_to_parse[:start]
                    in_multiline_comment = True
                    break
            
            # 移除行尾 // 注释
            if '//' in line_to_parse:
                line_to_parse = line_to_parse[:line_to_parse.index('//')]
            
            stripped = line_to_parse.strip()
            if not stripped:
                continue
            
            # Import
            if match := re.search(self.IMPORT_PATTERN, stripped):
                imports.append(match.group(1))
                continue
            
            # Package
            if match := re.search(self.PACKAGE_PATTERN, stripped):
                continue
            
            # Class
            if match := re.search(self.CLASS_PATTERN, stripped):
                class_name = match.group(1)
                class_names.add(class_name)
                symbols.append(SymbolInfo(name=class_name, type='class', line=i))
            
            # Interface
            elif match := re.search(self.INTERFACE_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='interface', line=i))
            
            # Enum
            elif match := re.search(self.ENUM_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='enum', line=i))
            
            # Record (Java 14+)
            elif match := re.search(self.RECORD_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='record', line=i))
            
            # Annotation type
            elif match := re.search(self.ANNOTATION_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='annotation', line=i))
            
            # Constant (UPPER_CASE naming)
            elif match := re.search(self.CONSTANT_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='const', line=i))
            
            # Method（排除构造函数和关键字）
            elif match := re.search(self.METHOD_PATTERN, stripped):
                method_name = match.group(1)
                # 排除关键字和构造函数（与类同名）
                if method_name not in excluded and method_name not in class_names:
                    symbols.append(SymbolInfo(name=method_name, type='method', line=i))
        
        return FileAnalysis(
            path=str(file_path),
            language='Java',
            lines=lines,
            symbols=symbols,
            imports=list(set(imports)),
        )
