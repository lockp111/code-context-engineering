
import unittest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent.parent / 'scripts'))

from analyzer.parsers.python import PythonASTAnalyzer
from analyzer.parsers.javascript import JSTypeScriptAnalyzer
from analyzer.parsers.typescript import TypeScriptAnalyzer
from analyzer.parsers.go import GoAnalyzer
from analyzer.parsers.rust import RustAnalyzer
from analyzer.parsers.cpp import CppAnalyzer
from analyzer.parsers.php import PhpAnalyzer

class TestParsers(unittest.TestCase):
    def setUp(self):
        # Locate project root and fixtures directory
        self.project_root = Path(__file__).parent.parent
        self.codes_dir = self.project_root / 'tests/codes'
        if not self.codes_dir.exists():
            self.skipTest("Fixtures directory not found at {}".format(self.codes_dir))

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
        
        # Methods (currently parsed as functions by AST walker)
        self.assertIn("method_one", symbols)
        self.assertIn("async_method", symbols)
        self.assertIn("__init__", symbols)

    def test_javascript_parser(self):
        path = self.codes_dir / "demo.js"
        analyzer = JSTypeScriptAnalyzer()
        result = analyzer.analyze(path)
        
        symbols = {s.name: s.type for s in result.symbols}
        
        # Classes
        self.assertIn("JSClass", symbols)
        self.assertEqual(symbols["JSClass"], "class")
        
        # Functions
        self.assertIn("method", symbols) # Method inside class
        self.assertIn("regularFunc", symbols)
        self.assertIn("arrowFunc", symbols)
        self.assertIn("asyncFunc", symbols)
        self.assertIn("internalArrow", symbols)

    def test_typescript_parser(self):
        path = self.codes_dir / "demo.ts"
        analyzer = TypeScriptAnalyzer()
        result = analyzer.analyze(path)
        
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
        analyzer = GoAnalyzer()
        result = analyzer.analyze(path)
        
        symbols = {s.name: s.type for s in result.symbols}
        
        # Structs and Interfaces
        self.assertIn("MyStruct", symbols)
        self.assertEqual(symbols["MyStruct"], "struct")
        self.assertIn("MyInterface", symbols)
        self.assertEqual(symbols["MyInterface"], "interface")
        
        # Functions and Methods
        self.assertIn("Function", symbols)
        self.assertEqual(symbols["Function"], "function")
        self.assertIn("Method", symbols) # Method on struct
        self.assertEqual(symbols["Method"], "function")

    def test_rust_parser(self):
        path = self.codes_dir / "demo.rs"
        analyzer = RustAnalyzer()
        result = analyzer.analyze(path)
        
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
        self.assertIn("new", symbols) # Impl method
        self.assertIn("trait_method", symbols) # Trait method definition
        
        # Impl blocks (captured as class type in current parser logic)
        self.assertTrue(any(s.startswith("impl") for s in symbols))

    def test_cpp_parser(self):
        path = self.codes_dir / "demo.cpp"
        analyzer = CppAnalyzer()
        result = analyzer.analyze(path)
        
        symbols = {s.name: s.type for s in result.symbols}
        
        # Classes and Structs
        self.assertIn("MyClass", symbols)
        self.assertEqual(symbols["MyClass"], "class")
        self.assertIn("MyStruct", symbols)
        self.assertEqual(symbols["MyStruct"], "struct")
        
        # Functions
        # Note: simplistic regex might miss some complex signatures or methods inside classes depending on indentation
        self.assertIn("templateFunc", symbols)
        self.assertIn("my_func", symbols)

    def test_php_parser(self):
        path = self.codes_dir / "demo.php"
        analyzer = PhpAnalyzer()
        result = analyzer.analyze(path)
        
        symbols = {s.name: s.type for s in result.symbols}
        
        # Classes, Interfaces, Traits
        self.assertIn("MyClass", symbols)
        self.assertEqual(symbols["MyClass"], "class")
        self.assertIn("AbstractClass", symbols)
        self.assertIn("MyInterface", symbols)
        self.assertEqual(symbols["MyInterface"], "interface")
        self.assertIn("MyTrait", symbols)
        self.assertEqual(symbols["MyTrait"], "trait")
        
        # Functions
        self.assertIn("my_func", symbols)
        self.assertIn("method", symbols)
        self.assertIn("abstractMethod", symbols)
        self.assertIn("traitMethod", symbols)

if __name__ == '__main__':
    unittest.main()
