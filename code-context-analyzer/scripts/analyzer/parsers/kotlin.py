import re
from pathlib import Path
from ..core import FileAnalysis, SymbolInfo

class KotlinAnalyzer:
    """Kotlin 语言分析器（基于正则）"""
    
    # 通用修饰符（顺序无关）- 移除了 fun 和 enum，它们有专门的模式
    MODIFIERS = r'(?:(?:public|private|protected|internal|open|final|abstract|sealed|override|lateinit|const|data|inline|noinline|crossinline|suspend|infix|operator|tailrec|external|inner|value|annotation|actual|expect)\s+)*'
    
    # 导入（支持通配符）
    IMPORT_PATTERN = r'^\s*import\s+([^\s]+)(?:\s+as\s+\w+)?'
    PACKAGE_PATTERN = r'^\s*package\s+([^\s]+)'
    
    # 类/接口/对象（修饰符顺序无关）
    CLASS_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)'
    DATA_CLASS_PATTERN = rf'^\s*{MODIFIERS}data\s+class\s+(\w+)'
    SEALED_CLASS_PATTERN = rf'^\s*{MODIFIERS}sealed\s+class\s+(\w+)'
    SEALED_INTERFACE_PATTERN = rf'^\s*{MODIFIERS}sealed\s+interface\s+(\w+)'
    VALUE_CLASS_PATTERN = rf'^\s*{MODIFIERS}value\s+class\s+(\w+)'
    INTERFACE_PATTERN = rf'^\s*{MODIFIERS}interface\s+(\w+)'
    FUN_INTERFACE_PATTERN = rf'^\s*{MODIFIERS}fun\s+interface\s+(\w+)'  # SAM 接口
    OBJECT_PATTERN = rf'^\s*{MODIFIERS}object\s+(\w+)'
    COMPANION_PATTERN = r'^\s*companion\s+object(?:\s+(\w+))?'
    ENUM_CLASS_PATTERN = rf'^\s*{MODIFIERS}enum\s+class\s+(\w+)'
    ANNOTATION_CLASS_PATTERN = rf'^\s*{MODIFIERS}annotation\s+class\s+(\w+)'
    
    # 函数（支持泛型、suspend、扩展函数等）
    FUNCTION_PATTERN = rf'^\s*(?:@\w+(?:\([^)]*\))?\s+)*{MODIFIERS}fun\s+(?:<[^>]+>\s+)?(?:[\w<>,\s]+\.)?(\w+)\s*(?:<[^>]+>)?\s*\('
    
    # 常量 (const val) - 必须在属性之前匹配
    CONST_PATTERN = rf'^\s*{MODIFIERS}const\s+val\s+(\w+)'
    
    # 顶层属性（val/var 在行首或只有少量缩进）
    TOP_LEVEL_PROPERTY_PATTERN = rf'^(?:@\w+(?:\([^)]*\))?\s+)*{MODIFIERS}(?:val|var)\s+(?:<[^>]+>\s+)?(\w+)\s*(?::\s*[^=]+)?(?:\s*=|\s*$|\s*by\s+)'
    
    # 类型别名
    TYPEALIAS_PATTERN = rf'^\s*{MODIFIERS}typealias\s+(\w+)'
    
    def _remove_string_literals(self, line: str) -> str:
        """移除字符串字面量，避免字符串内容干扰解析"""
        result = []
        i = 0
        in_string = False
        string_char = None
        
        while i < len(line):
            char = line[i]
            
            # 处理转义字符
            if i > 0 and line[i-1] == '\\' and in_string:
                i += 1
                continue
            
            # 检测三引号字符串开始
            if not in_string and i + 2 < len(line) and line[i:i+3] == '"""':
                in_string = True
                string_char = '"""'
                result.append('""')  # 保留空字符串占位
                i += 3
                # 跳过三引号字符串内容直到结束
                while i < len(line):
                    if i + 2 < len(line) and line[i:i+3] == '"""':
                        result.append('""')
                        i += 3
                        in_string = False
                        string_char = None
                        break
                    i += 1
                continue
            
            # 检测普通字符串
            if not in_string and char in '"\'':
                in_string = True
                string_char = char
                result.append(char)
                i += 1
                continue
            
            if in_string and char == string_char:
                in_string = False
                string_char = None
                result.append(char)
                i += 1
                continue
            
            if not in_string:
                result.append(char)
            
            i += 1
        
        return ''.join(result)
    
    def analyze(self, file_path: Path) -> FileAnalysis:
        """分析 Kotlin 文件"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines_list = content.splitlines()
            lines = len(lines_list)
        except UnicodeDecodeError:
            return FileAnalysis(path=str(file_path), language='Kotlin', lines=0)
        
        symbols = []
        imports = []
        in_multiline_comment = False
        in_multiline_string = False
        
        # 排除的函数名（关键字）
        excluded = {'if', 'for', 'while', 'when', 'catch', 'return', 'throw', 'try', 'else'}
        
        for i, line in enumerate(lines_list, 1):
            line_to_parse = line
            
            # 处理多行字符串（三引号）
            if in_multiline_string:
                if '"""' in line_to_parse:
                    idx = line_to_parse.index('"""')
                    line_to_parse = line_to_parse[idx + 3:]
                    in_multiline_string = False
                else:
                    continue
            
            # 检测多行字符串开始
            if '"""' in line_to_parse:
                # 计算三引号数量，奇数个表示进入/退出多行字符串
                count = line_to_parse.count('"""')
                if count % 2 == 1:
                    in_multiline_string = True
                    # 只保留第一个 """ 之前的内容
                    line_to_parse = line_to_parse[:line_to_parse.index('"""')]
            
            # 处理多行注释状态
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
            
            # 移除字符串字面量后再检测 // 注释
            line_without_strings = self._remove_string_literals(line_to_parse)
            if '//' in line_without_strings:
                # 找到真正的注释位置
                comment_pos = line_without_strings.index('//')
                line_to_parse = line_to_parse[:comment_pos]
            
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
            
            # Annotation class (必须在普通 class 之前检测)
            if match := re.search(self.ANNOTATION_CLASS_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='annotation', line=i))
                continue
            
            # Enum class (必须在普通 class 之前检测)
            if match := re.search(self.ENUM_CLASS_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='enum', line=i))
                continue
            
            # Data class (必须在普通 class 之前检测)
            if match := re.search(self.DATA_CLASS_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='data_class', line=i))
                continue
            
            # Sealed class (必须在普通 class 之前检测)
            if match := re.search(self.SEALED_CLASS_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='sealed_class', line=i))
                continue
            
            # Sealed interface
            if match := re.search(self.SEALED_INTERFACE_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='sealed_interface', line=i))
                continue
            
            # Value class (必须在普通 class 之前检测)
            if match := re.search(self.VALUE_CLASS_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='value_class', line=i))
                continue
            
            # Fun interface (SAM，必须在普通 interface 和 function 之前检测)
            if match := re.search(self.FUN_INTERFACE_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='fun_interface', line=i))
                continue
            
            # Class
            if match := re.search(self.CLASS_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='class', line=i))
                continue
            
            # Interface
            if match := re.search(self.INTERFACE_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='interface', line=i))
                continue
            
            # Companion object
            if match := re.search(self.COMPANION_PATTERN, stripped):
                name = match.group(1) if match.group(1) else 'Companion'
                symbols.append(SymbolInfo(name=name, type='companion', line=i))
                continue
            
            # Object
            if match := re.search(self.OBJECT_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='object', line=i))
                continue
            
            # Typealias
            if match := re.search(self.TYPEALIAS_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='typealias', line=i))
                continue
            
            # Const (常量，必须在普通属性之前)
            if match := re.search(self.CONST_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='const', line=i))
                continue
            
            # Function（排除关键字）
            if match := re.search(self.FUNCTION_PATTERN, stripped):
                func_name = match.group(1)
                if func_name not in excluded:
                    symbols.append(SymbolInfo(name=func_name, type='function', line=i))
                continue
            
            # 顶层属性 - 只匹配没有缩进的行（真正的顶层声明）
            # 使用原始行检测缩进
            if not line.startswith((' ', '\t')):
                if match := re.search(self.TOP_LEVEL_PROPERTY_PATTERN, stripped):
                    prop_name = match.group(1)
                    symbols.append(SymbolInfo(name=prop_name, type='property', line=i))
        
        return FileAnalysis(
            path=str(file_path),
            language='Kotlin',
            lines=lines,
            symbols=symbols,
            imports=list(set(imports)),
        )
