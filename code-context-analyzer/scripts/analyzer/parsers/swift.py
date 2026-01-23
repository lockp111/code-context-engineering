import re
from pathlib import Path
from ..core import FileAnalysis, SymbolInfo

class SwiftAnalyzer:
    """Swift 语言分析器（基于正则）"""
    
    # 通用修饰符（顺序无关）
    MODIFIERS = r'(?:(?:public|private|fileprivate|internal|open|final|static|class|override|mutating|nonmutating|required|convenience|lazy|weak|unowned|@\w+)\s+)*'
    
    # 导入
    IMPORT_PATTERN = r'^\s*import\s+(\w+)'
    
    # 类型定义
    CLASS_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)'
    STRUCT_PATTERN = rf'^\s*{MODIFIERS}struct\s+(\w+)'
    ENUM_PATTERN = rf'^\s*{MODIFIERS}enum\s+(\w+)'
    PROTOCOL_PATTERN = rf'^\s*{MODIFIERS}protocol\s+(\w+)'
    EXTENSION_PATTERN = rf'^\s*{MODIFIERS}extension\s+(\w+)'
    ACTOR_PATTERN = rf'^\s*{MODIFIERS}actor\s+(\w+)'
    
    # 函数/方法
    FUNC_PATTERN = rf'^\s*{MODIFIERS}func\s+(\w+)'
    INIT_PATTERN = rf'^\s*{MODIFIERS}init\s*[?\(]'
    
    # 类型别名
    TYPEALIAS_PATTERN = rf'^\s*{MODIFIERS}typealias\s+(\w+)\s*='
    
    # 属性包装器
    PROPERTY_WRAPPER_PATTERN = r'^\s*@propertyWrapper\s*$'
    
    def analyze(self, file_path: Path) -> FileAnalysis:
        """分析 Swift 文件"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines_list = content.splitlines()
            lines = len(lines_list)
        except UnicodeDecodeError:
            return FileAnalysis(path=str(file_path), language='Swift', lines=0)
        
        symbols = []
        imports = []
        in_multiline_comment = False
        next_is_property_wrapper = False
        
        for i, line in enumerate(lines_list, 1):
            line_to_parse = line
            
            # 处理多行注释
            if in_multiline_comment:
                if '*/' in line_to_parse:
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
                    line_to_parse = line_to_parse[:start]
                    in_multiline_comment = True
                    break
            
            # 移除行尾 // 注释
            if '//' in line_to_parse:
                line_to_parse = line_to_parse[:line_to_parse.index('//')]
            
            stripped = line_to_parse.strip()
            if not stripped:
                continue
            
            # 检查 @propertyWrapper 标记
            if re.search(self.PROPERTY_WRAPPER_PATTERN, stripped):
                next_is_property_wrapper = True
                continue
            
            # Import
            if match := re.search(self.IMPORT_PATTERN, stripped):
                imports.append(match.group(1))
                continue
            
            # Class
            if match := re.search(self.CLASS_PATTERN, stripped):
                symbol_type = 'property_wrapper' if next_is_property_wrapper else 'class'
                symbols.append(SymbolInfo(name=match.group(1), type=symbol_type, line=i))
                next_is_property_wrapper = False
            
            # Struct
            elif match := re.search(self.STRUCT_PATTERN, stripped):
                symbol_type = 'property_wrapper' if next_is_property_wrapper else 'struct'
                symbols.append(SymbolInfo(name=match.group(1), type=symbol_type, line=i))
                next_is_property_wrapper = False
            
            # Enum
            elif match := re.search(self.ENUM_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='enum', line=i))
                next_is_property_wrapper = False
            
            # Protocol
            elif match := re.search(self.PROTOCOL_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='protocol', line=i))
                next_is_property_wrapper = False
            
            # Extension
            elif match := re.search(self.EXTENSION_PATTERN, stripped):
                symbols.append(SymbolInfo(name=f"extension {match.group(1)}", type='extension', line=i))
                next_is_property_wrapper = False
            
            # Actor (Swift 5.5+)
            elif match := re.search(self.ACTOR_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='actor', line=i))
                next_is_property_wrapper = False
            
            # Typealias
            elif match := re.search(self.TYPEALIAS_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='typealias', line=i))
                next_is_property_wrapper = False
            
            # Init
            elif re.search(self.INIT_PATTERN, stripped):
                symbols.append(SymbolInfo(name='init', type='function', line=i))
                next_is_property_wrapper = False
            
            # Function
            elif match := re.search(self.FUNC_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='function', line=i))
                next_is_property_wrapper = False
            
            else:
                # 如果这行不是类型定义，重置 property wrapper 标记
                if next_is_property_wrapper and stripped and not stripped.startswith('@'):
                    next_is_property_wrapper = False
        
        return FileAnalysis(
            path=str(file_path),
            language='Swift',
            lines=lines,
            symbols=symbols,
            imports=list(set(imports)),
        )
