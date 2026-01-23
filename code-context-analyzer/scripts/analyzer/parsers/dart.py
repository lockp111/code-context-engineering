import re
from pathlib import Path
from ..core import FileAnalysis, SymbolInfo

class DartAnalyzer:
    """Dart/Flutter 语言分析器（基于正则）"""
    
    # 通用修饰符（顺序无关）
    MODIFIERS = r'(?:(?:abstract|base|final|interface|sealed|mixin|late|required|covariant|static|const|external|factory)\s+)*'
    
    # 导入和导出
    IMPORT_PATTERN = r"^\s*import\s+['\"]([^'\"]+)['\"]"
    EXPORT_PATTERN = r"^\s*export\s+['\"]([^'\"]+)['\"]"
    PART_PATTERN = r"^\s*part\s+['\"]([^'\"]+)['\"]"
    PART_OF_PATTERN = r"^\s*part\s+of\s+['\"]?([^'\";\s]+)['\"]?"
    LIBRARY_PATTERN = r'^\s*library\s+(\w+(?:\.\w+)*)'
    
    # 类定义（支持 abstract, base, final, interface, sealed, mixin class）
    CLASS_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)'
    ABSTRACT_CLASS_PATTERN = rf'^\s*abstract\s+{MODIFIERS}class\s+(\w+)'
    BASE_CLASS_PATTERN = rf'^\s*base\s+{MODIFIERS}class\s+(\w+)'
    FINAL_CLASS_PATTERN = rf'^\s*final\s+{MODIFIERS}class\s+(\w+)'
    INTERFACE_CLASS_PATTERN = rf'^\s*interface\s+{MODIFIERS}class\s+(\w+)'
    SEALED_CLASS_PATTERN = rf'^\s*sealed\s+{MODIFIERS}class\s+(\w+)'
    MIXIN_CLASS_PATTERN = rf'^\s*mixin\s+class\s+(\w+)'
    
    # Mixin 定义
    MIXIN_PATTERN = rf'^\s*{MODIFIERS}mixin\s+(\w+)(?:\s+on\s+|\s*\{{)'
    
    # 枚举定义
    ENUM_PATTERN = rf'^\s*enum\s+(\w+)'
    
    # Extension 定义（支持泛型）
    EXTENSION_PATTERN = r'^\s*extension\s+(\w+)?(?:<[^>]+>)?\s+on\s+(\w+)'
    
    # Extension Type 定义 (Dart 3.3+)
    EXTENSION_TYPE_PATTERN = rf'^\s*{MODIFIERS}extension\s+type\s+(\w+)'
    
    # Typedef 定义
    TYPEDEF_PATTERN = r'^\s*typedef\s+(\w+)'
    
    # 函数/方法定义（捕获返回类型以便后续检查，支持可空类型）
    FUNCTION_PATTERN = rf'^\s*{MODIFIERS}((?:Future<[^>]+>|Stream<[^>]+>|\w+(?:<[^>]+>)?)\??)\s+(\w+)\s*(?:<[^>]+>)?\s*\('
    VOID_FUNCTION_PATTERN = rf'^\s*{MODIFIERS}void\s+(\w+)\s*(?:<[^>]+>)?\s*\('
    
    # 排除作为返回类型的关键字
    EXCLUDED_RETURN_TYPES = {
        'return', 'if', 'for', 'while', 'switch', 'catch', 'throw', 'try', 'else',
        'const', 'final', 'var', 'late', 'new', 'this', 'super', 'await', 'yield',
        'class', 'enum', 'extension', 'typedef', 'import', 'export', 'library', 'part',
        'abstract', 'base', 'sealed', 'interface', 'mixin', 'extends', 'implements', 'with',
    }
    GETTER_PATTERN = rf'^\s*{MODIFIERS}(?:\w+(?:<[^>]+>)?)\s+get\s+(\w+)'
    SETTER_PATTERN = rf'^\s*{MODIFIERS}set\s+(\w+)\s*\('
    
    # 构造函数
    CONSTRUCTOR_PATTERN = r'^\s*(?:const\s+|factory\s+)?(\w+)\s*\.\s*(\w+)\s*\('  # Named constructor
    FACTORY_PATTERN = r'^\s*factory\s+(\w+)\s*(?:\.\s*(\w+))?\s*\('
    # 默认构造函数（没有返回类型，类名后直接是括号）
    DEFAULT_CONSTRUCTOR_PATTERN = r'^\s*(?:const\s+|external\s+)?(\w+)\s*\([^)]*\)\s*(?::|;|{)'
    
    # 顶层常量和变量
    CONST_PATTERN = r'^\s*const\s+(?:\w+(?:<[^>]+>)?\s+)?(\w+)\s*='
    FINAL_PATTERN = r'^\s*final\s+(?:\w+(?:<[^>]+>)?\s+)?(\w+)\s*='
    VAR_PATTERN = r'^\s*(?:var|late\s+(?:final\s+)?)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*='
    
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
            if not in_string and i + 2 < len(line):
                triple = line[i:i+3]
                if triple in ('"""', "'''"):
                    in_string = True
                    string_char = triple
                    result.append('""')
                    i += 3
                    while i < len(line):
                        if i + 2 < len(line) and line[i:i+3] == string_char:
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
            
            if in_string and string_char and len(string_char) == 1 and char == string_char:
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
        """分析 Dart 文件"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines_list = content.splitlines()
            lines = len(lines_list)
        except UnicodeDecodeError:
            return FileAnalysis(path=str(file_path), language='Dart', lines=0)
        
        symbols = []
        imports = []
        in_multiline_comment = False
        in_multiline_string = False
        multiline_string_char = None
        
        # 排除的函数名（关键字和修饰符 - 防止 const Result() 被识别为函数）
        excluded = {
            'if', 'for', 'while', 'switch', 'catch', 'return', 'throw', 'try', 'else', 'main',
            # 这些修饰符如果出现在"返回类型"位置会导致误识别
            'const', 'final', 'var', 'late', 'static', 'abstract', 'base', 'sealed', 
            'interface', 'mixin', 'required', 'covariant', 'external', 'factory',
            'class', 'enum', 'extension', 'typedef', 'import', 'export', 'part', 'library'
        }
        
        for i, line in enumerate(lines_list, 1):
            line_to_parse = line
            
            # 处理多行字符串
            if in_multiline_string:
                if multiline_string_char and multiline_string_char in line_to_parse:
                    idx = line_to_parse.index(multiline_string_char)
                    line_to_parse = line_to_parse[idx + len(multiline_string_char):]
                    in_multiline_string = False
                    multiline_string_char = None
                else:
                    continue
            
            # 检测多行字符串开始
            for triple in ('"""', "'''"):
                if triple in line_to_parse:
                    count = line_to_parse.count(triple)
                    if count % 2 == 1:
                        in_multiline_string = True
                        multiline_string_char = triple
                        line_to_parse = line_to_parse[:line_to_parse.index(triple)]
                        break
            
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
            
            # 移除字符串字面量后再检测 // 注释
            line_without_strings = self._remove_string_literals(line_to_parse)
            if '//' in line_without_strings:
                comment_pos = line_without_strings.index('//')
                line_to_parse = line_to_parse[:comment_pos]
            
            stripped = line_to_parse.strip()
            if not stripped:
                continue
            
            # Import
            if match := re.search(self.IMPORT_PATTERN, stripped):
                imports.append(match.group(1))
                continue
            
            # Export
            if match := re.search(self.EXPORT_PATTERN, stripped):
                continue
            
            # Part
            if match := re.search(self.PART_PATTERN, stripped):
                continue
            
            # Part of
            if match := re.search(self.PART_OF_PATTERN, stripped):
                continue
            
            # Library
            if match := re.search(self.LIBRARY_PATTERN, stripped):
                continue
            
            # Extension Type (Dart 3.3+，必须在 Extension 之前检测)
            if match := re.search(self.EXTENSION_TYPE_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='extension_type', line=i))
                continue
            
            # Mixin class (必须在普通 class 和 mixin 之前检测)
            if match := re.search(self.MIXIN_CLASS_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='mixin_class', line=i))
                continue
            
            # Sealed class (必须在普通 class 之前检测)
            if match := re.search(self.SEALED_CLASS_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='sealed_class', line=i))
                continue
            
            # Interface class (必须在普通 class 之前检测)
            if match := re.search(self.INTERFACE_CLASS_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='interface_class', line=i))
                continue
            
            # Final class (必须在普通 class 之前检测)
            if match := re.search(self.FINAL_CLASS_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='final_class', line=i))
                continue
            
            # Base class (必须在普通 class 之前检测)
            if match := re.search(self.BASE_CLASS_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='base_class', line=i))
                continue
            
            # Abstract class (必须在普通 class 之前检测)
            if match := re.search(self.ABSTRACT_CLASS_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='abstract_class', line=i))
                continue
            
            # Class
            if match := re.search(self.CLASS_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='class', line=i))
                continue
            
            # Mixin
            if match := re.search(self.MIXIN_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='mixin', line=i))
                continue
            
            # Enum
            if match := re.search(self.ENUM_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='enum', line=i))
                continue
            
            # Extension
            if match := re.search(self.EXTENSION_PATTERN, stripped):
                ext_name = match.group(1) if match.group(1) else f"on {match.group(2)}"
                symbols.append(SymbolInfo(name=ext_name, type='extension', line=i))
                continue
            
            # Typedef
            if match := re.search(self.TYPEDEF_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='typedef', line=i))
                continue
            
            # Factory constructor
            if match := re.search(self.FACTORY_PATTERN, stripped):
                if match.group(2):
                    name = f"{match.group(1)}.{match.group(2)}"
                else:
                    name = f"{match.group(1)}.factory"
                symbols.append(SymbolInfo(name=name, type='factory', line=i))
                continue
            
            # Named constructor
            if match := re.search(self.CONSTRUCTOR_PATTERN, stripped):
                name = f"{match.group(1)}.{match.group(2)}"
                symbols.append(SymbolInfo(name=name, type='constructor', line=i))
                continue
            
            # 默认构造函数（跳过，不添加到符号表，但需要先检测以避免被误识别为函数）
            if re.search(self.DEFAULT_CONSTRUCTOR_PATTERN, stripped):
                continue
            
            # Getter
            if match := re.search(self.GETTER_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='getter', line=i))
                continue
            
            # Setter
            if match := re.search(self.SETTER_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='setter', line=i))
                continue
            
            # Void function
            if match := re.search(self.VOID_FUNCTION_PATTERN, stripped):
                func_name = match.group(1)
                if func_name not in excluded:
                    symbols.append(SymbolInfo(name=func_name, type='function', line=i))
                continue
            
            # Function
            if match := re.search(self.FUNCTION_PATTERN, stripped):
                return_type = match.group(1)
                func_name = match.group(2)
                # 检查返回类型和函数名是否在排除列表中
                if return_type not in self.EXCLUDED_RETURN_TYPES and func_name not in excluded:
                    symbols.append(SymbolInfo(name=func_name, type='function', line=i))
                continue
            
            # 顶层常量/变量 - 只匹配没有缩进的行
            if not line.startswith((' ', '\t')):
                # Const
                if match := re.search(self.CONST_PATTERN, stripped):
                    symbols.append(SymbolInfo(name=match.group(1), type='const', line=i))
                    continue
                
                # Final
                if match := re.search(self.FINAL_PATTERN, stripped):
                    symbols.append(SymbolInfo(name=match.group(1), type='final', line=i))
                    continue
        
        return FileAnalysis(
            path=str(file_path),
            language='Dart',
            lines=lines,
            symbols=symbols,
            imports=list(set(imports)),
        )
