"""
Language-specific tree-sitter node type configurations.

Each language config defines:
- symbol_node_types: mapping of tree-sitter node types -> symbol category
- import_node_types: node types that represent import statements
- export_node_types: node types for exports (JS/TS only)
- name_field: the field name used to extract identifier names
"""

# ============================================================================
# JavaScript
# ============================================================================
JAVASCRIPT_CONFIG = {
    "symbol_types": {
        "class_declaration": "class",
        "function_declaration": "function",
        "generator_function_declaration": "function",
        "method_definition": "method",
        # Arrow functions assigned to const/let/var
        "lexical_declaration": "_check_arrow",
        "variable_declaration": "_check_arrow",
    },
    "import_types": ["import_statement"],
    "export_types": ["export_statement"],
}

# ============================================================================
# TypeScript (extends JavaScript)
# ============================================================================
TYPESCRIPT_CONFIG = {
    "symbol_types": {
        **JAVASCRIPT_CONFIG["symbol_types"],
        "interface_declaration": "interface",
        "type_alias_declaration": "type",
        "enum_declaration": "enum",
        "abstract_class_declaration": "class",
    },
    "import_types": ["import_statement"],
    "export_types": ["export_statement"],
}

# ============================================================================
# Go
# ============================================================================
GO_CONFIG = {
    "symbol_types": {
        "function_declaration": "function",
        "method_declaration": "method",
        "type_declaration": "_check_go_type",  # struct, interface, or type alias
    },
    "import_types": ["import_declaration"],
    "export_types": [],
}

# ============================================================================
# Rust
# ============================================================================
RUST_CONFIG = {
    "symbol_types": {
        "function_item": "function",
        "struct_item": "struct",
        "enum_item": "enum",
        "trait_item": "trait",
        "impl_item": "impl",
    },
    "import_types": ["use_declaration"],
    "export_types": [],
}

# ============================================================================
# C / C++
# ============================================================================
CPP_CONFIG = {
    "symbol_types": {
        "function_definition": "function",
        "declaration": "_check_cpp_declaration",
        "class_specifier": "class",
        "struct_specifier": "struct",
        "enum_specifier": "enum",
        "namespace_definition": "namespace",
    },
    "import_types": ["preproc_include"],
    "export_types": [],
}

# ============================================================================
# PHP
# ============================================================================
PHP_CONFIG = {
    "symbol_types": {
        "class_declaration": "class",
        "interface_declaration": "interface",
        "trait_declaration": "trait",
        "function_definition": "function",
        "method_declaration": "method",
    },
    "import_types": ["namespace_use_declaration"],
    "export_types": [],
}

# ============================================================================
# Java
# ============================================================================
JAVA_CONFIG = {
    "symbol_types": {
        "class_declaration": "class",
        "interface_declaration": "interface",
        "enum_declaration": "enum",
        "record_declaration": "class",
        "annotation_type_declaration": "class",
        "method_declaration": "method",
        "constructor_declaration": "method",
    },
    "import_types": ["import_declaration"],
    "export_types": [],
}

# ============================================================================
# Swift
# ============================================================================
SWIFT_CONFIG = {
    "symbol_types": {
        "class_declaration": "class",
        "struct_declaration": "struct",  # Added for Swift struct
        "protocol_declaration": "interface",
        "enum_declaration": "enum",
        "function_declaration": "function",
        "actor_declaration": "class",  # Swift actor
    },
    "import_types": ["import_declaration"],
    "export_types": [],
}

# ============================================================================
# Kotlin
# ============================================================================
KOTLIN_CONFIG = {
    "symbol_types": {
        "class_declaration": "class",
        "object_declaration": "class",
        "function_declaration": "function",
    },
    "import_types": ["import_header"],
    "export_types": [],
}

# ============================================================================
# Dart
# ============================================================================
DART_CONFIG = {
    "symbol_types": {
        "class_definition": "class",
        "mixin_declaration": "mixin",
        "enum_declaration": "enum",
        "extension_declaration": "extension",
        "extension_type_declaration": "extension_type",
        "type_alias": "typedef",
        "function_signature": "_check_dart_function",
        "method_signature": "method",
    },
    "import_types": ["import_or_export"],
    "export_types": [],
}

# ============================================================================
# Language name -> config mapping
# ============================================================================
LANG_CONFIGS = {
    "javascript": JAVASCRIPT_CONFIG,
    "typescript": TYPESCRIPT_CONFIG,
    "go": GO_CONFIG,
    "rust": RUST_CONFIG,
    "c": CPP_CONFIG,
    "cpp": CPP_CONFIG,
    "php": PHP_CONFIG,
    "java": JAVA_CONFIG,
    "swift": SWIFT_CONFIG,
    "kotlin": KOTLIN_CONFIG,
    "dart": DART_CONFIG,
}
