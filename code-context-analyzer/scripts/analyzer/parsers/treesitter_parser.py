"""
Unified tree-sitter based parser for all non-Python languages.

Replaces 11 regex-based parsers with accurate AST parsing that correctly
ignores comments, strings, and template literals.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, List, Dict, Any

import tree_sitter

from ..core import FileAnalysis, SymbolInfo
from .lang_queries import LANG_CONFIGS

# ============================================================================
# Language loader — lazy-init each language only once
# ============================================================================
_PARSERS: Dict[str, tree_sitter.Parser] = {}


def _get_parser(lang_key: str) -> tree_sitter.Parser:
    """Get or create a tree-sitter Parser for the given language key."""
    if lang_key in _PARSERS:
        return _PARSERS[lang_key]

    lang_obj = _load_language(lang_key)
    if lang_obj is None:
        raise ValueError(f"Unsupported language: {lang_key}")

    parser = tree_sitter.Parser(lang_obj)
    _PARSERS[lang_key] = parser
    return parser


def _load_language(lang_key: str) -> Optional[tree_sitter.Language]:
    """Load a tree-sitter Language object for the given key."""
    try:
        from tree_sitter_language_pack import get_language

        return get_language(lang_key)
    except (ImportError, KeyError):
        return None


# ============================================================================
# Extension -> (language_key, display_name) mapping
# ============================================================================
EXT_TO_LANG = {
    ".js": ("javascript", "JavaScript"),
    ".jsx": ("javascript", "JavaScript (React)"),
    ".ts": ("typescript", "TypeScript"),
    ".tsx": ("tsx", "TypeScript (React)"),
    ".go": ("go", "Go"),
    ".rs": ("rust", "Rust"),
    ".c": ("c", "C"),
    ".h": ("c", "C"),
    ".cpp": ("cpp", "C++"),
    ".cc": ("cpp", "C++"),
    ".cxx": ("cpp", "C++"),
    ".hpp": ("cpp", "C++"),
    ".hxx": ("cpp", "C++"),
    ".hh": ("cpp", "C++"),
    ".php": ("php", "PHP"),
    ".java": ("java", "Java"),
    ".swift": ("swift", "Swift"),
    ".kt": ("kotlin", "Kotlin"),
    ".dart": ("dart", "Dart"),
}


# ============================================================================
# Main parser class
# ============================================================================
class TreeSitterParser:
    """
    Unified tree-sitter based parser.

    Provides the same `analyze(file_path) -> FileAnalysis` interface
    as the old regex parsers, but with accurate AST-based parsing.
    """

    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser supports the given file extension."""
        return file_path.suffix.lower() in EXT_TO_LANG

    def analyze(self, file_path: Path) -> FileAnalysis:
        """Analyze a source file using tree-sitter."""
        ext = file_path.suffix.lower()
        if ext not in EXT_TO_LANG:
            return FileAnalysis(path=str(file_path), language="Unknown", lines=0)

        lang_key, display_name = EXT_TO_LANG[ext]

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = len(content.splitlines())
        except (UnicodeDecodeError, OSError):
            return FileAnalysis(path=str(file_path), language=display_name, lines=0)

        try:
            parser = _get_parser(lang_key)
        except (ValueError, ImportError):
            # Fallback: return basic info without symbols
            return FileAnalysis(path=str(file_path), language=display_name, lines=lines)

        tree = parser.parse(content.encode("utf-8"))
        root = tree.root_node

        # Use the config for this language (tsx/typescript share the same config)
        config_key = "typescript" if lang_key == "tsx" else lang_key
        config = LANG_CONFIGS.get(config_key, {})

        symbols = []
        imports = []
        exports = []

        self._extract_symbols(root, config, symbols, lang_key)
        self._extract_imports(root, config, imports, lang_key)
        self._extract_exports(root, config, exports)

        return FileAnalysis(
            path=str(file_path),
            language=display_name,
            lines=lines,
            symbols=symbols,
            imports=list(set(imports)),
            exports=exports,
        )

    # ========================================================================
    # Symbol extraction
    # ========================================================================
    def _extract_symbols(
        self,
        node: Any,
        config: dict,
        symbols: List[SymbolInfo],
        lang_key: str,
        parent_class: str = "",
    ):
        """Recursively extract symbols from the AST."""
        symbol_types = config.get("symbol_types", {})

        for child in node.children:
            node_type = child.type

            if node_type in symbol_types:
                sym_type = symbol_types[node_type]

                if sym_type == "_check_arrow":
                    self._handle_arrow_function(child, symbols)
                elif sym_type == "_check_go_type":
                    self._handle_go_type(child, symbols)
                elif sym_type == "_check_dart_function":
                    self._handle_dart_function(child, symbols)
                elif sym_type == "_check_cpp_declaration":
                    pass  # Skip complex C++ declarations for now
                elif sym_type == "impl":
                    self._handle_rust_impl(child, symbols)
                elif sym_type == "method":
                    name = self._get_name(child, lang_key)
                    if name:
                        symbols.append(
                            SymbolInfo(
                                name=name,
                                type="method",
                                line=child.start_point[0] + 1,
                                end_line=child.end_point[0] + 1,
                                parameters=self._get_parameters(child),
                                decorators=self._get_decorators(child),
                            )
                        )
                else:
                    name = self._get_name(child, lang_key)
                    if name:
                        symbols.append(
                            SymbolInfo(
                                name=name,
                                type=sym_type,
                                line=child.start_point[0] + 1,
                                end_line=child.end_point[0] + 1,
                                parameters=(
                                    self._get_parameters(child)
                                    if sym_type == "function"
                                    else []
                                ),
                                decorators=self._get_decorators(child),
                            )
                        )

                # Recurse into class bodies for methods
                if sym_type in ("class", "interface", "struct", "trait"):
                    class_name = self._get_name(child, lang_key)
                    self._extract_symbols(
                        child, config, symbols, lang_key, class_name or ""
                    )
                elif sym_type not in ("method", "_check_arrow"):
                    # Recurse into other containers (namespaces, etc.)
                    self._extract_symbols(
                        child, config, symbols, lang_key, parent_class
                    )
            else:
                # Recurse into nodes we don't directly handle
                self._extract_symbols(child, config, symbols, lang_key, parent_class)

    # ========================================================================
    # Name extraction
    # ========================================================================
    def _get_name(self, node: Any, lang_key: str) -> Optional[str]:
        """Extract the identifier name from a declaration node."""
        # Try common field names
        for field in ("name", "identifier"):
            child = node.child_by_field_name(field)
            if child:
                return child.text.decode("utf-8")

        # Fallback: find the first identifier child
        for child in node.children:
            if child.type in (
                "identifier",
                "property_identifier",
                "type_identifier",
                "simple_identifier",
            ):
                return child.text.decode("utf-8")

        return None

    # ========================================================================
    # Parameter extraction
    # ========================================================================
    def _get_parameters(self, node: Any) -> List[str]:
        """Extract function/method parameters."""
        params = []
        # Find the formal_parameters / parameter_list node
        param_node = node.child_by_field_name("parameters")
        if param_node is None:
            # Search for parameter-like children
            for child in node.children:
                if child.type in (
                    "formal_parameters",
                    "parameter_list",
                    "function_value_parameters",
                    "formal_parameter_list",  # Dart
                ):
                    param_node = child
                    break

        if param_node is None:
            return params

        for child in param_node.children:
            if child.type in ("identifier", "simple_identifier"):
                params.append(child.text.decode("utf-8"))
            elif child.type in (
                "formal_parameter",
                "required_parameter",
                "optional_parameter",
                "parameter",
                "parameter_declaration",
                "simple_parameter",
                "default_parameter",  # Dart
            ):
                # Get the name from within the parameter node
                name = self._get_param_name(child)
                if name and name != "self" and name != "this":
                    params.append(name)

        return params[:10]  # Limit to 10 params

    def _get_param_name(self, node: Any) -> Optional[str]:
        """Extract parameter name from a parameter node."""
        # Try 'name' field first
        name_node = node.child_by_field_name("name")
        if name_node:
            return name_node.text.decode("utf-8")
        # Try 'pattern' field (TypeScript)
        pattern_node = node.child_by_field_name("pattern")
        if pattern_node and pattern_node.type == "identifier":
            return pattern_node.text.decode("utf-8")
        # Fallback: first identifier child
        for child in node.children:
            if child.type in ("identifier", "simple_identifier"):
                return child.text.decode("utf-8")
        return None

    # ========================================================================
    # Decorator extraction
    # ========================================================================
    def _get_decorators(self, node: Any) -> List[str]:
        """Extract decorators/annotations from a node."""
        decorators = []
        # Check previous siblings and children for decorators
        for child in node.children:
            if child.type in ("decorator", "annotation", "attribute"):
                dec_name = self._get_decorator_name(child)
                if dec_name:
                    decorators.append(dec_name)
        return decorators

    def _get_decorator_name(self, node: Any) -> Optional[str]:
        """Extract the name from a decorator node."""
        for child in node.children:
            if child.type in ("identifier", "call_expression"):
                if child.type == "call_expression":
                    func = child.child_by_field_name("function")
                    if func:
                        return func.text.decode("utf-8")
                return child.text.decode("utf-8")
        return None

    # ========================================================================
    # Import extraction
    # ========================================================================
    def _extract_imports(
        self, node: Any, config: dict, imports: List[str], lang_key: str
    ):
        """Extract import statements from the AST."""
        import_types = config.get("import_types", [])

        for child in node.children:
            if child.type in import_types:
                imp = self._parse_import(child, lang_key)
                if imp:
                    imports.extend(imp)
            else:
                # Recurse into children (skip function bodies for efficiency)
                if child.type not in (
                    "function_declaration",
                    "class_declaration",
                    "method_definition",
                    "function_definition",
                    "class_body",
                    "block",
                ):
                    self._extract_imports(child, config, imports, lang_key)

    def _parse_import(self, node: Any, lang_key: str) -> List[str]:
        """Parse an import statement node into module names."""
        results = []

        if lang_key in ("javascript", "typescript", "tsx"):
            # JS/TS: import X from 'module' / require('module')
            source = node.child_by_field_name("source")
            if source:
                mod = source.text.decode("utf-8").strip("'\"")
                results.append(mod)
            else:
                # Dynamic import or require
                for child in node.children:
                    if child.type == "string":
                        mod = child.text.decode("utf-8").strip("'\"")
                        results.append(mod)

        elif lang_key == "go":
            # Go: import "pkg" or import ( "pkg1" "pkg2" )
            for child in node.children:
                if child.type == "import_spec":
                    path_node = child.child_by_field_name("path")
                    if path_node:
                        results.append(path_node.text.decode("utf-8").strip('"'))
                elif child.type == "import_spec_list":
                    for spec in child.children:
                        if spec.type == "import_spec":
                            path_node = spec.child_by_field_name("path")
                            if path_node:
                                results.append(
                                    path_node.text.decode("utf-8").strip('"')
                                )
                elif child.type == "interpreted_string_literal":
                    results.append(child.text.decode("utf-8").strip('"'))

        elif lang_key == "rust":
            # Rust: use crate::module;
            # Extract the first path segment
            text = node.text.decode("utf-8")
            # Remove 'use ' prefix and ';' suffix
            path = text.replace("use ", "").rstrip(";").strip()
            if "::" in path:
                results.append(path.split("::")[0])
            else:
                results.append(path)

        elif lang_key in ("c", "cpp"):
            # C/C++: #include <file> or #include "file"
            for child in node.children:
                if child.type in ("string_literal", "system_lib_string"):
                    inc = child.text.decode("utf-8").strip('<>"')
                    results.append(inc)

        elif lang_key == "php":
            # PHP: use Namespace\Class;
            text = node.text.decode("utf-8")
            text = text.replace("use ", "").rstrip(";").strip()
            results.append(text)

        elif lang_key == "java":
            # Java: import package.Class;
            for child in node.children:
                if child.type == "scoped_identifier":
                    results.append(child.text.decode("utf-8"))
                    break

        elif lang_key == "swift":
            # Swift: import Module
            for child in node.children:
                if child.type == "identifier":
                    results.append(child.text.decode("utf-8"))

        elif lang_key == "kotlin":
            # Kotlin: import package.Class
            for child in node.children:
                if child.type == "identifier":
                    results.append(child.text.decode("utf-8"))
                    break
        elif lang_key == "dart":
            # Dart: import 'package:path/to/file.dart';
            # Structure: import_or_export → library_import → import_specification
            #            → configurable_uri → uri → string_literal
            self._find_dart_import_strings(node, results)

        return results

    # ========================================================================
    # Export extraction (JS/TS only)
    # ========================================================================
    def _extract_exports(self, node: Any, config: dict, exports: List[str]):
        """Extract export statements (JS/TS)."""
        export_types = config.get("export_types", [])
        if not export_types:
            return

        for child in node.children:
            if child.type in export_types:
                # Find the exported name
                for sub in child.children:
                    if sub.type in (
                        "class_declaration",
                        "function_declaration",
                        "generator_function_declaration",
                        "abstract_class_declaration",
                        "interface_declaration",
                        "type_alias_declaration",
                        "enum_declaration",
                    ):
                        name_node = sub.child_by_field_name("name")
                        if name_node:
                            exports.append(name_node.text.decode("utf-8"))
                    elif sub.type == "lexical_declaration":
                        for decl in sub.children:
                            if decl.type == "variable_declarator":
                                name_node = decl.child_by_field_name("name")
                                if name_node:
                                    exports.append(name_node.text.decode("utf-8"))
                    elif sub.type == "export_clause":
                        for spec in sub.children:
                            if spec.type == "export_specifier":
                                name_node = spec.child_by_field_name("name")
                                if name_node:
                                    exports.append(name_node.text.decode("utf-8"))

    # ========================================================================
    # Language-specific handlers
    # ========================================================================
    def _handle_arrow_function(self, node: Any, symbols: List[SymbolInfo]):
        """Handle const/let/var declarations that may contain arrow functions."""
        for child in node.children:
            if child.type == "variable_declarator":
                name_node = child.child_by_field_name("name")
                value_node = child.child_by_field_name("value")
                if name_node and value_node and value_node.type == "arrow_function":
                    symbols.append(
                        SymbolInfo(
                            name=name_node.text.decode("utf-8"),
                            type="function",
                            line=child.start_point[0] + 1,
                            end_line=child.end_point[0] + 1,
                            parameters=self._get_parameters(value_node),
                        )
                    )

    def _handle_go_type(self, node: Any, symbols: List[SymbolInfo]):
        """Handle Go type declarations (struct, interface, alias)."""
        for child in node.children:
            if child.type == "type_spec":
                name_node = child.child_by_field_name("name")
                type_node = child.child_by_field_name("type")
                if name_node and type_node:
                    name = name_node.text.decode("utf-8")
                    if type_node.type == "struct_type":
                        sym_type = "struct"
                    elif type_node.type == "interface_type":
                        sym_type = "interface"
                    else:
                        sym_type = "type"
                    symbols.append(
                        SymbolInfo(
                            name=name,
                            type=sym_type,
                            line=child.start_point[0] + 1,
                            end_line=child.end_point[0] + 1,
                        )
                    )

    def _handle_rust_impl(self, node: Any, symbols: List[SymbolInfo]):
        """Handle Rust impl blocks."""
        name_node = node.child_by_field_name("type")
        name = name_node.text.decode("utf-8") if name_node else None
        if name:
            symbols.append(
                SymbolInfo(
                    name=f"impl {name}",
                    type="class",
                    line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                )
            )

    def _handle_dart_function(self, node: Any, symbols: List[SymbolInfo]):
        """Handle Dart function_signature nodes (top-level functions)."""
        # function_signature: return_type name(params)
        # The identifier is the function name (not the return type)
        name = None
        for child in node.children:
            if child.type == "identifier":
                name = child.text.decode("utf-8")
            elif child.type == "formal_parameter_list":
                break  # Name comes before params
        if name:
            symbols.append(
                SymbolInfo(
                    name=name,
                    type="function",
                    line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parameters=self._get_parameters(node),
                )
            )

    def _find_dart_import_strings(self, node: Any, results: List[str]):
        """Recursively find string_literal nodes inside Dart import_or_export."""
        for child in node.children:
            if child.type == "string_literal":
                mod = child.text.decode("utf-8").strip("'\"")
                if mod:
                    results.append(mod)
            else:
                self._find_dart_import_strings(child, results)
