import unittest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent.parent / "code-context-analyzer" / "scripts"))

from analyzer.parsers.python import PythonASTAnalyzer
from analyzer.parsers.javascript import JSTypeScriptAnalyzer
from analyzer.parsers.typescript import TypeScriptAnalyzer
from analyzer.parsers.go import GoAnalyzer
from analyzer.parsers.rust import RustAnalyzer
from analyzer.parsers.cpp import CppAnalyzer
from analyzer.parsers.php import PhpAnalyzer
from analyzer.parsers.java import JavaAnalyzer
from analyzer.parsers.swift import SwiftAnalyzer
from analyzer.parsers.kotlin import KotlinAnalyzer
from analyzer.parsers.dart import DartAnalyzer
from analyzer.parsers.flutter import FlutterAnalyzer


class TestParsers(unittest.TestCase):
    def setUp(self):
        # Locate project root and fixtures directory
        self.project_root = Path(__file__).parent.parent
        self.codes_dir = self.project_root / "tests/codes"
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
        self.assertIn("method", symbols)  # Method inside class
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
        self.assertIn("Method", symbols)  # Method on struct
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
        self.assertIn("new", symbols)  # Impl method
        self.assertIn("trait_method", symbols)  # Trait method definition

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

    def test_java_parser(self):
        path = self.codes_dir / "demo.java"
        analyzer = JavaAnalyzer()
        result = analyzer.analyze(path)

        symbols = {s.name: s.type for s in result.symbols}

        # Interfaces
        self.assertIn("UserService", symbols)
        self.assertEqual(symbols["UserService"], "interface")

        # Classes (including abstract)
        self.assertIn("BaseEntity", symbols)
        self.assertEqual(symbols["BaseEntity"], "class")
        self.assertIn("User", symbols)
        self.assertEqual(symbols["User"], "class")

        # Enums
        self.assertIn("UserStatus", symbols)
        self.assertEqual(symbols["UserStatus"], "enum")

        # Records (Java 14+)
        self.assertIn("UserDTO", symbols)
        self.assertEqual(symbols["UserDTO"], "record")

        # Annotations
        self.assertIn("Validated", symbols)
        self.assertEqual(symbols["Validated"], "annotation")

        # Methods
        self.assertIn("findById", symbols)
        self.assertIn("getUsername", symbols)
        self.assertIn("findFirst", symbols)

        # Imports
        self.assertIn("java.util.List", result.imports)
        self.assertIn("java.util.Optional", result.imports)

    def test_swift_parser(self):
        path = self.codes_dir / "demo.swift"
        analyzer = SwiftAnalyzer()
        result = analyzer.analyze(path)

        symbols = {s.name: s.type for s in result.symbols}

        # Protocols
        self.assertIn("Drawable", symbols)
        self.assertEqual(symbols["Drawable"], "protocol")
        self.assertIn("DataSource", symbols)
        self.assertEqual(symbols["DataSource"], "protocol")

        # Enums
        self.assertIn("Direction", symbols)
        self.assertEqual(symbols["Direction"], "enum")
        self.assertIn("Result", symbols)
        self.assertEqual(symbols["Result"], "enum")

        # Structs
        self.assertIn("Point", symbols)
        self.assertEqual(symbols["Point"], "struct")

        # Classes
        self.assertIn("Shape", symbols)
        self.assertEqual(symbols["Shape"], "class")
        self.assertIn("Circle", symbols)
        self.assertEqual(symbols["Circle"], "class")

        # Extensions
        self.assertIn("extension String", symbols)
        self.assertEqual(symbols["extension String"], "extension")

        # Actor (Swift 5.5+)
        self.assertIn("DataManager", symbols)
        self.assertEqual(symbols["DataManager"], "actor")

        # Typealias
        self.assertIn("CompletionHandler", symbols)
        self.assertEqual(symbols["CompletionHandler"], "typealias")
        self.assertIn("JSON", symbols)
        self.assertEqual(symbols["JSON"], "typealias")

        # Property Wrapper
        self.assertIn("Clamped", symbols)
        self.assertEqual(symbols["Clamped"], "property_wrapper")

        # Functions
        self.assertIn("draw", symbols)
        self.assertIn("fetchData", symbols)

        # Imports
        self.assertIn("Foundation", result.imports)
        self.assertIn("UIKit", result.imports)

    def test_kotlin_parser(self):
        path = self.codes_dir / "demo.kt"
        analyzer = KotlinAnalyzer()
        result = analyzer.analyze(path)

        symbols = {s.name: s.type for s in result.symbols}

        # Interfaces
        self.assertIn("UserService", symbols)
        self.assertEqual(symbols["UserService"], "interface")

        # Fun interface (SAM)
        self.assertIn("Callback", symbols)
        self.assertEqual(symbols["Callback"], "fun_interface")

        # Sealed interface
        self.assertIn("State", symbols)
        self.assertEqual(symbols["State"], "sealed_interface")

        # Classes (including abstract and open)
        self.assertIn("BaseEntity", symbols)
        self.assertEqual(symbols["BaseEntity"], "class")
        self.assertIn("User", symbols)
        self.assertEqual(symbols["User"], "class")

        # Data class
        self.assertIn("UserDTO", symbols)
        self.assertEqual(symbols["UserDTO"], "data_class")

        # Sealed class
        self.assertIn("Result", symbols)
        self.assertEqual(symbols["Result"], "sealed_class")

        # Value class
        self.assertIn("UserId", symbols)
        self.assertEqual(symbols["UserId"], "value_class")

        # Enum class
        self.assertIn("UserStatus", symbols)
        self.assertEqual(symbols["UserStatus"], "enum")

        # Annotation class
        self.assertIn("Validated", symbols)
        self.assertEqual(symbols["Validated"], "annotation")

        # Object (singleton)
        self.assertIn("UserRepository", symbols)
        self.assertEqual(symbols["UserRepository"], "object")

        # Companion object
        self.assertIn("Companion", symbols)
        self.assertEqual(symbols["Companion"], "companion")
        self.assertIn("Factory", symbols)
        self.assertEqual(symbols["Factory"], "companion")

        # Functions
        self.assertIn("findById", symbols)
        self.assertIn("fetchData", symbols)
        self.assertIn("isValidEmail", symbols)  # Extension function
        self.assertIn("findFirst", symbols)  # Generic function
        self.assertIn("parseJson", symbols)  # Inline function
        self.assertIn("times", symbols)  # Infix function

        # Typealias
        self.assertIn("UserList", symbols)
        self.assertEqual(symbols["UserList"], "typealias")
        self.assertIn("CompletionHandler", symbols)
        self.assertEqual(symbols["CompletionHandler"], "typealias")

        # Constants
        self.assertIn("MAX_NAME_LENGTH", symbols)
        self.assertEqual(symbols["MAX_NAME_LENGTH"], "const")

        # Top-level properties (including those with // in string values)
        self.assertIn("VERSION", symbols)
        self.assertEqual(symbols["VERSION"], "property")
        self.assertIn("url", symbols)  # 字符串中的 // 不应被当作注释
        self.assertIn("regex", symbols)

        # Imports
        self.assertIn("kotlin.collections.List", result.imports)
        self.assertIn("kotlinx.coroutines.flow.Flow", result.imports)
        self.assertIn("java.util.Optional", result.imports)


    def test_dart_parser(self):
        path = self.codes_dir / "demo.dart"
        analyzer = DartAnalyzer()
        result = analyzer.analyze(path)

        symbols = {s.name: s.type for s in result.symbols}

        # Typedef
        self.assertIn("JsonMap", symbols)
        self.assertEqual(symbols["JsonMap"], "typedef")
        self.assertIn("VoidCallback", symbols)
        self.assertEqual(symbols["VoidCallback"], "typedef")
        self.assertIn("AsyncCallback", symbols)
        self.assertEqual(symbols["AsyncCallback"], "typedef")

        # Enum
        self.assertIn("UserStatus", symbols)
        self.assertEqual(symbols["UserStatus"], "enum")
        self.assertIn("HttpMethod", symbols)
        self.assertEqual(symbols["HttpMethod"], "enum")

        # Mixin
        self.assertIn("Loggable", symbols)
        self.assertEqual(symbols["Loggable"], "mixin")
        self.assertIn("Serializable", symbols)
        self.assertEqual(symbols["Serializable"], "mixin")

        # Abstract class
        self.assertIn("BaseEntity", symbols)
        self.assertEqual(symbols["BaseEntity"], "abstract_class")

        # Sealed class (Dart 3.0+)
        self.assertIn("Result", symbols)
        self.assertEqual(symbols["Result"], "sealed_class")

        # Final class (Dart 3.0+)
        self.assertIn("Success", symbols)
        self.assertEqual(symbols["Success"], "final_class")
        self.assertIn("Failure", symbols)
        self.assertEqual(symbols["Failure"], "final_class")

        # Interface class (Dart 3.0+)
        self.assertIn("UserRepository", symbols)
        self.assertEqual(symbols["UserRepository"], "interface_class")

        # Base class (Dart 3.0+)
        self.assertIn("Animal", symbols)
        self.assertEqual(symbols["Animal"], "base_class")

        # Mixin class (Dart 3.0+)
        self.assertIn("Walker", symbols)
        self.assertEqual(symbols["Walker"], "mixin_class")

        # Regular classes
        self.assertIn("User", symbols)
        self.assertEqual(symbols["User"], "class")
        self.assertIn("UserProfileWidget", symbols)
        self.assertEqual(symbols["UserProfileWidget"], "class")
        self.assertIn("_UserProfileWidgetState", symbols)
        self.assertEqual(symbols["_UserProfileWidgetState"], "class")
        self.assertIn("UserCard", symbols)
        self.assertEqual(symbols["UserCard"], "class")
        self.assertIn("Configuration", symbols)
        self.assertEqual(symbols["Configuration"], "class")

        # Named constructor
        self.assertIn("User.guest", symbols)
        self.assertEqual(symbols["User.guest"], "constructor")

        # Factory constructor
        self.assertIn("User.fromJson", symbols)
        self.assertEqual(symbols["User.fromJson"], "factory")

        # Extension
        self.assertIn("StringExtension", symbols)
        self.assertEqual(symbols["StringExtension"], "extension")
        self.assertIn("ListExtension", symbols)
        self.assertEqual(symbols["ListExtension"], "extension")

        # Extension Type (Dart 3.3+)
        self.assertIn("UserId", symbols)
        self.assertEqual(symbols["UserId"], "extension_type")
        self.assertIn("Email", symbols)
        self.assertEqual(symbols["Email"], "extension_type")

        # Functions
        self.assertIn("fetchUser", symbols)
        self.assertEqual(symbols["fetchUser"], "function")
        self.assertIn("countStream", symbols)
        self.assertEqual(symbols["countStream"], "function")
        self.assertIn("printMessage", symbols)
        self.assertEqual(symbols["printMessage"], "function")
        self.assertIn("tryCast", symbols)
        self.assertEqual(symbols["tryCast"], "function")

        # Getter and Setter
        self.assertIn("apiUrl", symbols)
        self.assertIn("timeout", symbols)

        # Top-level constants
        self.assertIn("appName", symbols)
        self.assertEqual(symbols["appName"], "const")
        self.assertIn("maxRetries", symbols)
        self.assertEqual(symbols["maxRetries"], "const")
        self.assertIn("defaultPadding", symbols)
        self.assertEqual(symbols["defaultPadding"], "const")

        # Top-level final variables
        self.assertIn("appStartTime", symbols)
        self.assertEqual(symbols["appStartTime"], "final")
        self.assertIn("emailRegex", symbols)
        self.assertEqual(symbols["emailRegex"], "final")

        # Imports
        self.assertIn("dart:async", result.imports)
        self.assertIn("dart:convert", result.imports)
        self.assertIn("package:flutter/material.dart", result.imports)
        self.assertIn("package:flutter/widgets.dart", result.imports)

    def test_flutter_parser(self):
        path = self.codes_dir / "demo_flutter.dart"
        analyzer = FlutterAnalyzer()
        result = analyzer.analyze(path)

        symbols = {s.name: s.type for s in result.symbols}

        # Typedef
        self.assertIn("JsonMap", symbols)
        self.assertEqual(symbols["JsonMap"], "typedef")
        self.assertIn("WidgetBuilder", symbols)
        self.assertEqual(symbols["WidgetBuilder"], "typedef")

        # Enum
        self.assertIn("AppTheme", symbols)
        self.assertEqual(symbols["AppTheme"], "enum")
        self.assertIn("LoadingState", symbols)
        self.assertEqual(symbols["LoadingState"], "enum")

        # Mixin
        self.assertIn("LoggerMixin", symbols)
        self.assertEqual(symbols["LoggerMixin"], "mixin")

        # StatelessWidget
        self.assertIn("MyButton", symbols)
        self.assertEqual(symbols["MyButton"], "stateless_widget")
        self.assertIn("AppLogo", symbols)
        self.assertEqual(symbols["AppLogo"], "stateless_widget")

        # StatefulWidget
        self.assertIn("CounterPage", symbols)
        self.assertEqual(symbols["CounterPage"], "stateful_widget")
        self.assertIn("AnimatedCounter", symbols)
        self.assertEqual(symbols["AnimatedCounter"], "stateful_widget")

        # Widget State
        self.assertIn("_CounterPageState", symbols)
        self.assertEqual(symbols["_CounterPageState"], "widget_state")
        self.assertIn("_AnimatedCounterState", symbols)
        self.assertEqual(symbols["_AnimatedCounterState"], "widget_state")

        # InheritedWidget
        self.assertIn("ThemeProvider", symbols)
        self.assertEqual(symbols["ThemeProvider"], "inherited_widget")

        # InheritedModel
        self.assertIn("UserModel", symbols)
        self.assertEqual(symbols["UserModel"], "inherited_model")

        # ChangeNotifier
        self.assertIn("CounterNotifier", symbols)
        self.assertEqual(symbols["CounterNotifier"], "change_notifier")
        self.assertIn("UserNotifier", symbols)
        self.assertEqual(symbols["UserNotifier"], "change_notifier")

        # ValueNotifier
        self.assertIn("ThemeNotifier", symbols)
        self.assertEqual(symbols["ThemeNotifier"], "value_notifier")

        # Cubit (flutter_bloc)
        self.assertIn("CounterCubit", symbols)
        self.assertEqual(symbols["CounterCubit"], "cubit")

        # Bloc (flutter_bloc)
        self.assertIn("CounterBloc", symbols)
        self.assertEqual(symbols["CounterBloc"], "bloc")

        # Abstract class (Event)
        self.assertIn("CounterEvent", symbols)
        self.assertEqual(symbols["CounterEvent"], "abstract_class")

        # Regular class (Event implementations)
        self.assertIn("IncrementEvent", symbols)
        self.assertEqual(symbols["IncrementEvent"], "class")
        self.assertIn("DecrementEvent", symbols)
        self.assertEqual(symbols["DecrementEvent"], "class")

        # CustomPainter
        self.assertIn("CirclePainter", symbols)
        self.assertEqual(symbols["CirclePainter"], "custom_painter")
        self.assertIn("GridPainter", symbols)
        self.assertEqual(symbols["GridPainter"], "custom_painter")

        # Extension
        self.assertIn("BuildContextExtension", symbols)
        self.assertEqual(symbols["BuildContextExtension"], "extension")
        self.assertIn("WidgetExtension", symbols)
        self.assertEqual(symbols["WidgetExtension"], "extension")

        # Functions
        self.assertIn("buildLoadingWidget", symbols)
        self.assertEqual(symbols["buildLoadingWidget"], "function")
        self.assertIn("showSnackBar", symbols)
        self.assertEqual(symbols["showSnackBar"], "function")

        # Top-level constants
        self.assertIn("appName", symbols)
        self.assertEqual(symbols["appName"], "const")
        self.assertIn("defaultPadding", symbols)
        self.assertEqual(symbols["defaultPadding"], "const")
        self.assertIn("animationDuration", symbols)
        self.assertEqual(symbols["animationDuration"], "const")

        # Top-level final
        self.assertIn("lightTheme", symbols)
        self.assertEqual(symbols["lightTheme"], "final")
        self.assertIn("darkTheme", symbols)
        self.assertEqual(symbols["darkTheme"], "final")

        # Imports
        self.assertIn("dart:async", result.imports)
        self.assertIn("package:flutter/material.dart", result.imports)
        self.assertIn("package:flutter_bloc/flutter_bloc.dart", result.imports)
        self.assertIn("package:provider/provider.dart", result.imports)


if __name__ == "__main__":
    unittest.main()
