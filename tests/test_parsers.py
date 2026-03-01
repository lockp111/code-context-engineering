import unittest
import sys
import tempfile
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent.parent / "code-context-analyzer" / "scripts"))

from analyzer.parsers.python import PythonASTAnalyzer
from analyzer.parsers.treesitter_parser import TreeSitterParser


class TestParsers(unittest.TestCase):
    def setUp(self):
        # Locate project root and fixtures directory
        self.project_root = Path(__file__).parent.parent
        self.codes_dir = self.project_root / "tests/codes"
        if not self.codes_dir.exists():
            self.skipTest("Fixtures directory not found at {}".format(self.codes_dir))
        self.ts_parser = TreeSitterParser()

    def test_python_parser(self):
        path = self.codes_dir / "demo.py"
        analyzer = PythonASTAnalyzer()
        result = analyzer.analyze(path)

        symbols = {s.name: s.type for s in result.symbols}

        # Classes
        self.assertIn("MyClass", symbols)
        self.assertEqual(symbols["MyClass"], "class")

        # Functions (including async and decorated)
        self.assertIn("decorated_func", symbols)
        self.assertEqual(symbols["decorated_func"], "function")
        self.assertIn("async_main", symbols)
        self.assertEqual(symbols["async_main"], "function")

        # Methods — now correctly identified as 'method' (was 'function' before fix)
        self.assertIn("method_one", symbols)
        self.assertEqual(symbols["method_one"], "method")
        self.assertIn("async_method", symbols)
        self.assertEqual(symbols["async_method"], "method")
        self.assertIn("__init__", symbols)
        self.assertEqual(symbols["__init__"], "method")

    def test_javascript_parser(self):
        path = self.codes_dir / "demo.js"
        result = self.ts_parser.analyze(path)

        symbols = {s.name: s.type for s in result.symbols}

        # Classes
        self.assertIn("JSClass", symbols)
        self.assertEqual(symbols["JSClass"], "class")

        # Methods inside class
        self.assertIn("constructor", symbols)
        self.assertIn("method", symbols)

        # Functions
        self.assertIn("regularFunc", symbols)
        self.assertIn("arrowFunc", symbols)
        self.assertIn("asyncFunc", symbols)
        self.assertIn("internalArrow", symbols)

    def test_typescript_parser(self):
        path = self.codes_dir / "demo.ts"
        result = self.ts_parser.analyze(path)

        symbols = {s.name: s.type for s in result.symbols}

        # Interfaces and Types
        self.assertIn("IUser", symbols)
        self.assertEqual(symbols["IUser"], "interface")
        self.assertIn("UserID", symbols)
        self.assertEqual(symbols["UserID"], "type")
        self.assertIn("UserRole", symbols)
        self.assertEqual(symbols["UserRole"], "enum")

        # Classes
        self.assertIn("BaseService", symbols)
        self.assertIn("UserService", symbols)
        self.assertEqual(symbols["UserService"], "class")

        # Functions
        self.assertIn("helper", symbols)
        self.assertIn("arrowHelper", symbols)
        # Methods
        self.assertIn("getData", symbols)

    def test_go_parser(self):
        path = self.codes_dir / "demo.go"
        result = self.ts_parser.analyze(path)

        symbols = {s.name: s.type for s in result.symbols}

        # Structs and Interfaces
        self.assertIn("MyStruct", symbols)
        self.assertEqual(symbols["MyStruct"], "struct")
        self.assertIn("MyInterface", symbols)
        self.assertEqual(symbols["MyInterface"], "interface")

        # Functions
        self.assertIn("Function", symbols)
        self.assertEqual(symbols["Function"], "function")
        # Methods (tree-sitter distinguishes method_declaration)
        self.assertIn("Method", symbols)

    def test_rust_parser(self):
        path = self.codes_dir / "demo.rs"
        result = self.ts_parser.analyze(path)

        symbols = {s.name: s.type for s in result.symbols}

        # Structs, Enums, Traits
        self.assertIn("MyStruct", symbols)
        self.assertEqual(symbols["MyStruct"], "struct")
        self.assertIn("MyEnum", symbols)
        self.assertEqual(symbols["MyEnum"], "enum")
        self.assertIn("MyTrait", symbols)
        self.assertEqual(symbols["MyTrait"], "trait")

        # Functions
        self.assertIn("my_func", symbols)
        self.assertIn("new", symbols)

        # Impl blocks
        self.assertTrue(any(s.startswith("impl") for s in symbols))

    def test_cpp_parser(self):
        path = self.codes_dir / "demo.cpp"
        result = self.ts_parser.analyze(path)

        symbols = {s.name: s.type for s in result.symbols}

        # Classes and Structs
        self.assertIn("MyClass", symbols)
        self.assertEqual(symbols["MyClass"], "class")
        self.assertIn("MyStruct", symbols)
        self.assertEqual(symbols["MyStruct"], "struct")

    def test_php_parser(self):
        path = self.codes_dir / "demo.php"
        result = self.ts_parser.analyze(path)

        symbols = {s.name: s.type for s in result.symbols}

        # Classes, Interfaces, Traits
        self.assertIn("MyClass", symbols)
        self.assertEqual(symbols["MyClass"], "class")
        self.assertIn("AbstractClass", symbols)
        self.assertIn("MyInterface", symbols)
        self.assertEqual(symbols["MyInterface"], "interface")
        self.assertIn("MyTrait", symbols)
        self.assertEqual(symbols["MyTrait"], "trait")

        # Functions/Methods
        self.assertIn("my_func", symbols)

    def test_java_parser(self):
        path = self.codes_dir / "demo.java"
        result = self.ts_parser.analyze(path)

        symbols = {s.name: s.type for s in result.symbols}

        # Interfaces
        self.assertIn("UserService", symbols)
        self.assertEqual(symbols["UserService"], "interface")

        # Classes
        self.assertIn("BaseEntity", symbols)
        self.assertEqual(symbols["BaseEntity"], "class")
        # User appears both as class and constructor — check class exists
        user_types = [s.type for s in result.symbols if s.name == "User"]
        self.assertIn("class", user_types)

        # Enums
        self.assertIn("UserStatus", symbols)
        self.assertEqual(symbols["UserStatus"], "enum")

        # Records
        self.assertIn("UserDTO", symbols)
        self.assertEqual(symbols["UserDTO"], "class")

        # Methods
        self.assertIn("findById", symbols)
        self.assertIn("getUsername", symbols)

        # Imports
        self.assertIn("java.util.List", result.imports)

    def test_swift_parser(self):
        path = self.codes_dir / "demo.swift"
        result = self.ts_parser.analyze(path)

        symbols = {s.name: s.type for s in result.symbols}

        # Protocols (mapped as 'interface' in tree-sitter config)
        self.assertIn("Drawable", symbols)
        self.assertIn("DataSource", symbols)

        # Enums
        self.assertIn("Direction", symbols)
        self.assertIn("Result", symbols)

        # Structs
        self.assertIn("Point", symbols)

        # Classes
        self.assertIn("Shape", symbols)
        self.assertIn("Circle", symbols)

        # Functions
        self.assertIn("fetchData", symbols)

        # Imports
        self.assertIn("Foundation", result.imports)

    def test_kotlin_parser(self):
        path = self.codes_dir / "demo.kt"
        result = self.ts_parser.analyze(path)

        symbols = {s.name: s.type for s in result.symbols}

        # Classes
        self.assertIn("BaseEntity", symbols)
        self.assertIn("User", symbols)

        # Functions
        self.assertIn("findById", symbols)
        self.assertIn("fetchData", symbols)
        self.assertIn("isValidEmail", symbols)
        self.assertIn("findFirst", symbols)

    def test_dart_parser(self):
        path = self.codes_dir / "demo.dart"
        result = self.ts_parser.analyze(path)

        symbols = {s.name: s.type for s in result.symbols}

        # Typedef
        self.assertIn("JsonMap", symbols)
        self.assertEqual(symbols["JsonMap"], "typedef")

        # Enum
        self.assertIn("UserStatus", symbols)
        self.assertEqual(symbols["UserStatus"], "enum")
        self.assertIn("HttpMethod", symbols)
        self.assertEqual(symbols["HttpMethod"], "enum")

        # Mixin
        self.assertIn("Loggable", symbols)
        self.assertEqual(symbols["Loggable"], "mixin")

        # Classes (tree-sitter uses generic 'class' type)
        self.assertIn("User", symbols)
        self.assertEqual(symbols["User"], "class")
        self.assertIn("UserProfileWidget", symbols)
        self.assertEqual(symbols["UserProfileWidget"], "class")

        # Extensions
        self.assertIn("StringExtension", symbols)
        self.assertEqual(symbols["StringExtension"], "extension")

        # Extension types
        self.assertIn("UserId", symbols)
        self.assertEqual(symbols["UserId"], "extension_type")

        # Functions
        self.assertIn("printMessage", symbols)
        self.assertEqual(symbols["printMessage"], "function")

        # Imports
        self.assertIn("dart:async", result.imports)
        self.assertIn("dart:convert", result.imports)

        # Flutter widgets in demo.dart (StatefulWidget, StatelessWidget)
        self.assertIn("UserProfileWidget", symbols)
        self.assertEqual(symbols["UserProfileWidget"], "class")
        self.assertIn("UserCard", symbols)
        self.assertEqual(symbols["UserCard"], "class")


class TestTreeSitterAccuracy(unittest.TestCase):
    """Test that tree-sitter does not produce false positives from comments/strings."""

    def setUp(self):
        self.parser = TreeSitterParser()

    def test_js_no_false_positives_from_comments(self):
        """Comments and strings should not produce false symbol matches."""
        code = """
// class FakeClassInComment {}
// function fakeFunction() {}

/* class MultiLineComment {} */

const str = "function notAFunction() { class NotAClass {} }";

const template = `
  function templateFunction() {
    class TemplateClass {}
  }
`;

class RealClass {
  method() {}
}

function realFunction(a, b) { return a + b; }
"""
        with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            result = self.parser.analyze(Path(f.name))

        symbol_names = [s.name for s in result.symbols]

        # Real symbols should be found
        self.assertIn("RealClass", symbol_names)
        self.assertIn("realFunction", symbol_names)
        self.assertIn("method", symbol_names)

        # Fake symbols from comments/strings should NOT be found
        self.assertNotIn("FakeClassInComment", symbol_names)
        self.assertNotIn("fakeFunction", symbol_names)
        self.assertNotIn("MultiLineComment", symbol_names)
        self.assertNotIn("NotAClass", symbol_names)
        self.assertNotIn("templateFunction", symbol_names)
        self.assertNotIn("TemplateClass", symbol_names)

    def test_ts_no_false_positives(self):
        """TypeScript should also be immune to comment/string false positives."""
        code = """
// interface FakeInterface {}
const s = "class FakeClass {}";

interface RealInterface {
  method(): void;
}

type RealType = string;

class RealClass {}

function realFunction(): void {}
"""
        with tempfile.NamedTemporaryFile(suffix=".ts", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            result = self.parser.analyze(Path(f.name))

        symbol_names = [s.name for s in result.symbols]

        self.assertIn("RealInterface", symbol_names)
        self.assertIn("RealType", symbol_names)
        self.assertIn("RealClass", symbol_names)
        self.assertIn("realFunction", symbol_names)

        self.assertNotIn("FakeInterface", symbol_names)
        self.assertNotIn("FakeClass", symbol_names)

    def test_generator_functions(self):
        """Generator functions should be detected (was missed by regex)."""
        code = """
function* myGenerator() { yield 1; }
async function* asyncGen() { yield 2; }
"""
        with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            result = self.parser.analyze(Path(f.name))

        symbol_names = [s.name for s in result.symbols]
        self.assertIn("myGenerator", symbol_names)
        self.assertIn("asyncGen", symbol_names)


if __name__ == "__main__":
    unittest.main()
