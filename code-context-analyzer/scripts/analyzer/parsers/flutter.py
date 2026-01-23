import re
from pathlib import Path
from typing import Optional, Tuple
from ..core import FileAnalysis, SymbolInfo


class FlutterAnalyzer:
    """Flutter 框架分析器（基于正则）
    
    专门识别 Flutter 特定的组件和模式：
    - StatelessWidget / StatefulWidget / State
    - InheritedWidget / InheritedModel
    - ChangeNotifier / ValueNotifier
    - Provider / BLoC / Riverpod 相关模式
    - Flutter 特定注解
    """
    
    # 通用修饰符
    MODIFIERS = r'(?:(?:abstract|base|final|interface|sealed|mixin|late|required|covariant|static|const|external|factory)\s+)*'
    
    # 导入和导出
    IMPORT_PATTERN = r"^\s*import\s+['\"]([^'\"]+)['\"]"
    EXPORT_PATTERN = r"^\s*export\s+['\"]([^'\"]+)['\"]"
    PART_PATTERN = r"^\s*part\s+['\"]([^'\"]+)['\"]"
    PART_OF_PATTERN = r"^\s*part\s+of\s+['\"]?([^'\";\s]+)['\"]?"
    LIBRARY_PATTERN = r'^\s*library\s+(\w+(?:\.\w+)*)'
    
    # Flutter Widget 类型检测（继承关系）
    STATELESS_WIDGET_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)\s+extends\s+StatelessWidget'
    STATEFUL_WIDGET_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)\s+extends\s+StatefulWidget'
    STATE_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)\s+extends\s+State<(\w+)>'
    INHERITED_WIDGET_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)\s+extends\s+InheritedWidget'
    INHERITED_MODEL_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)\s+extends\s+InheritedModel'
    INHERITED_NOTIFIER_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)\s+extends\s+InheritedNotifier'
    
    # 状态管理相关
    CHANGE_NOTIFIER_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)\s+(?:extends|with)\s+.*ChangeNotifier'
    VALUE_NOTIFIER_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)\s+extends\s+ValueNotifier'
    CUBIT_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)\s+extends\s+Cubit<(\w+)>'
    BLOC_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)\s+extends\s+Bloc<(\w+),\s*(\w+)>'
    NOTIFIER_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)\s+extends\s+(?:Async)?Notifier<(\w+)>'
    STATE_NOTIFIER_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)\s+extends\s+StateNotifier<(\w+)>'
    
    # 其他常见 Flutter 基类
    CUSTOM_PAINTER_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)\s+extends\s+CustomPainter'
    CUSTOM_CLIPPER_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)\s+extends\s+CustomClipper'
    ROUTE_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)\s+extends\s+(?:Page)?Route(?:Builder)?'
    ANIMATION_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)\s+extends\s+(?:Animation|AnimationController|Tween)'
    RENDER_OBJECT_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)\s+extends\s+(?:Render\w+|SingleChildRenderObjectWidget|MultiChildRenderObjectWidget)'
    
    # 通用类定义（带继承检测）
    CLASS_EXTENDS_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)(?:<[^>]+>)?\s+extends\s+(\w+)'
    CLASS_WITH_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)(?:<[^>]+>)?\s+(?:extends\s+\w+(?:<[^>]+>)?\s+)?with\s+([^{{]+)'
    CLASS_IMPLEMENTS_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)(?:<[^>]+>)?\s+(?:extends[^{{]+)?implements\s+([^{{]+)'
    
    # 基础类定义
    CLASS_PATTERN = rf'^\s*{MODIFIERS}class\s+(\w+)'
    ABSTRACT_CLASS_PATTERN = rf'^\s*abstract\s+{MODIFIERS}class\s+(\w+)'
    
    # Mixin 定义
    MIXIN_PATTERN = rf'^\s*{MODIFIERS}mixin\s+(\w+)(?:\s+on\s+|\s*\{{)'
    
    # 枚举定义
    ENUM_PATTERN = rf'^\s*enum\s+(\w+)'
    
    # Extension 定义
    EXTENSION_PATTERN = r'^\s*extension\s+(\w+)?(?:<[^>]+>)?\s+on\s+(\w+)'
    EXTENSION_TYPE_PATTERN = rf'^\s*{MODIFIERS}extension\s+type\s+(\w+)'
    
    # Typedef 定义
    TYPEDEF_PATTERN = r'^\s*typedef\s+(\w+)'
    
    # 函数/方法定义
    FUNCTION_PATTERN = rf'^\s*{MODIFIERS}((?:Future<[^>]+>|Stream<[^>]+>|FutureOr<[^>]+>|\w+(?:<[^>]+>)?)\??)\s+(\w+)\s*(?:<[^>]+>)?\s*\('
    VOID_FUNCTION_PATTERN = rf'^\s*{MODIFIERS}void\s+(\w+)\s*(?:<[^>]+>)?\s*\('
    
    # 排除作为返回类型的关键字
    EXCLUDED_RETURN_TYPES = {
        'return', 'if', 'for', 'while', 'switch', 'catch', 'throw', 'try', 'else',
        'const', 'final', 'var', 'late', 'new', 'this', 'super', 'await', 'yield',
        'class', 'enum', 'extension', 'typedef', 'import', 'export', 'library', 'part',
        'abstract', 'base', 'sealed', 'interface', 'mixin', 'extends', 'implements', 'with',
    }
    
    # Getter/Setter
    GETTER_PATTERN = rf'^\s*{MODIFIERS}(?:\w+(?:<[^>]+>)?)\s+get\s+(\w+)'
    SETTER_PATTERN = rf'^\s*{MODIFIERS}set\s+(\w+)\s*\('
    
    # 构造函数
    CONSTRUCTOR_PATTERN = r'^\s*(?:const\s+|factory\s+)?(\w+)\s*\.\s*(\w+)\s*\('
    FACTORY_PATTERN = r'^\s*factory\s+(\w+)\s*(?:\.\s*(\w+))?\s*\('
    DEFAULT_CONSTRUCTOR_PATTERN = r'^\s*(?:const\s+|external\s+)?(\w+)\s*\([^)]*\)\s*(?::|;|{)'
    
    # 顶层常量和变量
    CONST_PATTERN = r'^\s*const\s+(?:\w+(?:<[^>]+>)?\s+)?(\w+)\s*='
    FINAL_PATTERN = r'^\s*final\s+(?:\w+(?:<[^>]+>)?\s+)?(\w+)\s*='
    
    # Flutter 特定注解
    FLUTTER_ANNOTATIONS = {
        '@override', '@protected', '@required', '@immutable', '@sealed',
        '@visibleForTesting', '@visibleForOverriding', '@mustCallSuper',
        '@optionalTypeArgs', '@factory', '@literal', '@virtual',
        '@nonVirtual', '@experimental', '@deprecated', '@Deprecated',
    }
    
    # Widget 基类映射
    WIDGET_BASE_CLASSES = {
        'StatelessWidget': 'stateless_widget',
        'StatefulWidget': 'stateful_widget',
        'InheritedWidget': 'inherited_widget',
        'InheritedModel': 'inherited_model',
        'InheritedNotifier': 'inherited_notifier',
        'RenderObjectWidget': 'render_object_widget',
        'SingleChildRenderObjectWidget': 'render_object_widget',
        'MultiChildRenderObjectWidget': 'render_object_widget',
        'LeafRenderObjectWidget': 'render_object_widget',
        'PreferredSizeWidget': 'widget',
    }
    
    # 状态管理基类映射
    STATE_MANAGEMENT_CLASSES = {
        'ChangeNotifier': 'change_notifier',
        'ValueNotifier': 'value_notifier',
        'Cubit': 'cubit',
        'Bloc': 'bloc',
        'Notifier': 'notifier',
        'AsyncNotifier': 'async_notifier',
        'StateNotifier': 'state_notifier',
    }
    
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
    
    def _detect_flutter_widget_type(self, stripped: str) -> Tuple[Optional[str], Optional[str]]:
        """检测 Flutter Widget 类型
        
        返回: (类名, 类型) 或 (None, None)
        """
        # StatelessWidget
        if match := re.search(self.STATELESS_WIDGET_PATTERN, stripped):
            return match.group(1), 'stateless_widget'
        
        # StatefulWidget
        if match := re.search(self.STATEFUL_WIDGET_PATTERN, stripped):
            return match.group(1), 'stateful_widget'
        
        # State<T>
        if match := re.search(self.STATE_PATTERN, stripped):
            return match.group(1), 'widget_state'
        
        # InheritedWidget
        if match := re.search(self.INHERITED_WIDGET_PATTERN, stripped):
            return match.group(1), 'inherited_widget'
        
        # InheritedModel
        if match := re.search(self.INHERITED_MODEL_PATTERN, stripped):
            return match.group(1), 'inherited_model'
        
        # InheritedNotifier
        if match := re.search(self.INHERITED_NOTIFIER_PATTERN, stripped):
            return match.group(1), 'inherited_notifier'
        
        return None, None
    
    def _detect_state_management_type(self, stripped: str) -> Tuple[Optional[str], Optional[str]]:
        """检测状态管理类型
        
        返回: (类名, 类型) 或 (None, None)
        """
        # ChangeNotifier
        if match := re.search(self.CHANGE_NOTIFIER_PATTERN, stripped):
            return match.group(1), 'change_notifier'
        
        # ValueNotifier
        if match := re.search(self.VALUE_NOTIFIER_PATTERN, stripped):
            return match.group(1), 'value_notifier'
        
        # Cubit (flutter_bloc)
        if match := re.search(self.CUBIT_PATTERN, stripped):
            return match.group(1), 'cubit'
        
        # Bloc (flutter_bloc)
        if match := re.search(self.BLOC_PATTERN, stripped):
            return match.group(1), 'bloc'
        
        # Notifier/AsyncNotifier (Riverpod)
        if match := re.search(self.NOTIFIER_PATTERN, stripped):
            return match.group(1), 'notifier'
        
        # StateNotifier (Riverpod legacy)
        if match := re.search(self.STATE_NOTIFIER_PATTERN, stripped):
            return match.group(1), 'state_notifier'
        
        return None, None
    
    def _detect_flutter_special_class(self, stripped: str) -> Tuple[Optional[str], Optional[str]]:
        """检测其他 Flutter 特殊类
        
        返回: (类名, 类型) 或 (None, None)
        """
        # CustomPainter
        if match := re.search(self.CUSTOM_PAINTER_PATTERN, stripped):
            return match.group(1), 'custom_painter'
        
        # CustomClipper
        if match := re.search(self.CUSTOM_CLIPPER_PATTERN, stripped):
            return match.group(1), 'custom_clipper'
        
        # Route
        if match := re.search(self.ROUTE_PATTERN, stripped):
            return match.group(1), 'route'
        
        # RenderObject 相关
        if match := re.search(self.RENDER_OBJECT_PATTERN, stripped):
            return match.group(1), 'render_object'
        
        return None, None
    
    def analyze(self, file_path: Path) -> FileAnalysis:
        """分析 Flutter 文件"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines_list = content.splitlines()
            lines = len(lines_list)
        except UnicodeDecodeError:
            return FileAnalysis(path=str(file_path), language='Flutter', lines=0)
        
        symbols = []
        imports = []
        flutter_imports = []
        in_multiline_comment = False
        in_multiline_string = False
        multiline_string_char = None
        
        # 排除的函数名
        excluded = {
            'if', 'for', 'while', 'switch', 'catch', 'return', 'throw', 'try', 'else', 'main',
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
                import_path = match.group(1)
                imports.append(import_path)
                # 检测 Flutter 相关导入
                if 'flutter' in import_path or 'package:' in import_path:
                    flutter_imports.append(import_path)
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
            
            # Extension Type (Dart 3.3+)
            if match := re.search(self.EXTENSION_TYPE_PATTERN, stripped):
                symbols.append(SymbolInfo(name=match.group(1), type='extension_type', line=i))
                continue
            
            # 检测 Flutter Widget 类型（必须在普通 class 之前）
            widget_name, widget_type = self._detect_flutter_widget_type(stripped)
            if widget_name and widget_type:
                symbols.append(SymbolInfo(name=widget_name, type=widget_type, line=i))
                continue
            
            # 检测状态管理类型（必须在普通 class 之前）
            state_name, state_type = self._detect_state_management_type(stripped)
            if state_name and state_type:
                symbols.append(SymbolInfo(name=state_name, type=state_type, line=i))
                continue
            
            # 检测其他 Flutter 特殊类（必须在普通 class 之前）
            special_name, special_type = self._detect_flutter_special_class(stripped)
            if special_name and special_type:
                symbols.append(SymbolInfo(name=special_name, type=special_type, line=i))
                continue
            
            # Abstract class
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
            
            # 默认构造函数
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
                if return_type not in self.EXCLUDED_RETURN_TYPES and func_name not in excluded:
                    symbols.append(SymbolInfo(name=func_name, type='function', line=i))
                continue
            
            # 顶层常量/变量
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
            language='Flutter',
            lines=lines,
            symbols=symbols,
            imports=list(set(imports)),
        )
