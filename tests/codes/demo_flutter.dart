import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:provider/provider.dart';

// =============================================================================
// Typedef
// =============================================================================
typedef JsonMap = Map<String, dynamic>;
typedef WidgetBuilder = Widget Function(BuildContext context);

// =============================================================================
// Enum
// =============================================================================
enum AppTheme { light, dark, system }

enum LoadingState { idle, loading, success, error }

// =============================================================================
// Mixin
// =============================================================================
mixin LoggerMixin {
  void log(String message) => debugPrint('[LOG] $message');
}

// =============================================================================
// StatelessWidget
// =============================================================================
class MyButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;

  const MyButton({super.key, required this.label, this.onPressed});

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: onPressed,
      child: Text(label),
    );
  }
}

class AppLogo extends StatelessWidget {
  const AppLogo({super.key});

  @override
  Widget build(BuildContext context) {
    return const FlutterLogo(size: 100);
  }
}

// =============================================================================
// StatefulWidget
// =============================================================================
class CounterPage extends StatefulWidget {
  final int initialValue;

  const CounterPage({super.key, this.initialValue = 0});

  @override
  State<CounterPage> createState() => _CounterPageState();
}

class _CounterPageState extends State<CounterPage> with LoggerMixin {
  late int _count;

  @override
  void initState() {
    super.initState();
    _count = widget.initialValue;
    log('Counter initialized with $_count');
  }

  void _increment() {
    setState(() => _count++);
  }

  void _decrement() {
    setState(() => _count--);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Count: $_count'),
        MyButton(label: '+', onPressed: _increment),
        MyButton(label: '-', onPressed: _decrement),
      ],
    );
  }
}

class AnimatedCounter extends StatefulWidget {
  const AnimatedCounter({super.key});

  @override
  State<AnimatedCounter> createState() => _AnimatedCounterState();
}

class _AnimatedCounterState extends State<AnimatedCounter>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 1),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) => Container(),
    );
  }
}

// =============================================================================
// InheritedWidget
// =============================================================================
class ThemeProvider extends InheritedWidget {
  final AppTheme theme;
  final void Function(AppTheme) setTheme;

  const ThemeProvider({
    super.key,
    required this.theme,
    required this.setTheme,
    required super.child,
  });

  static ThemeProvider? of(BuildContext context) {
    return context.dependOnInheritedWidgetOfExactType<ThemeProvider>();
  }

  @override
  bool updateShouldNotify(ThemeProvider oldWidget) {
    return theme != oldWidget.theme;
  }
}

// =============================================================================
// InheritedModel
// =============================================================================
class UserModel extends InheritedModel<String> {
  final String name;
  final String email;
  final int age;

  const UserModel({
    super.key,
    required this.name,
    required this.email,
    required this.age,
    required super.child,
  });

  static UserModel? of(BuildContext context, {String? aspect}) {
    return InheritedModel.inheritFrom<UserModel>(context, aspect: aspect);
  }

  @override
  bool updateShouldNotify(UserModel oldWidget) {
    return name != oldWidget.name ||
        email != oldWidget.email ||
        age != oldWidget.age;
  }

  @override
  bool updateShouldNotifyDependent(UserModel oldWidget, Set<String> aspects) {
    if (aspects.contains('name') && name != oldWidget.name) return true;
    if (aspects.contains('email') && email != oldWidget.email) return true;
    if (aspects.contains('age') && age != oldWidget.age) return true;
    return false;
  }
}

// =============================================================================
// ChangeNotifier (Provider pattern)
// =============================================================================
class CounterNotifier extends ChangeNotifier {
  int _count = 0;
  int get count => _count;

  void increment() {
    _count++;
    notifyListeners();
  }

  void decrement() {
    _count--;
    notifyListeners();
  }
}

class UserNotifier with ChangeNotifier {
  String _name = '';
  String get name => _name;

  void setName(String value) {
    _name = value;
    notifyListeners();
  }
}

// =============================================================================
// ValueNotifier
// =============================================================================
class ThemeNotifier extends ValueNotifier<AppTheme> {
  ThemeNotifier() : super(AppTheme.system);

  void toggle() {
    value = value == AppTheme.light ? AppTheme.dark : AppTheme.light;
  }
}

// =============================================================================
// Cubit (flutter_bloc)
// =============================================================================
class CounterCubit extends Cubit<int> {
  CounterCubit() : super(0);

  void increment() => emit(state + 1);
  void decrement() => emit(state - 1);
}

// =============================================================================
// Bloc (flutter_bloc)
// =============================================================================
abstract class CounterEvent {}
class IncrementEvent extends CounterEvent {}
class DecrementEvent extends CounterEvent {}

class CounterBloc extends Bloc<CounterEvent, int> {
  CounterBloc() : super(0) {
    on<IncrementEvent>((event, emit) => emit(state + 1));
    on<DecrementEvent>((event, emit) => emit(state - 1));
  }
}

// =============================================================================
// CustomPainter
// =============================================================================
class CirclePainter extends CustomPainter {
  final Color color;
  final double radius;

  CirclePainter({required this.color, required this.radius});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.fill;
    canvas.drawCircle(
      Offset(size.width / 2, size.height / 2),
      radius,
      paint,
    );
  }

  @override
  bool shouldRepaint(CirclePainter oldDelegate) {
    return color != oldDelegate.color || radius != oldDelegate.radius;
  }
}

class GridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    // Draw grid
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

// =============================================================================
// Extension
// =============================================================================
extension BuildContextExtension on BuildContext {
  ThemeData get theme => Theme.of(this);
  TextTheme get textTheme => theme.textTheme;
  ColorScheme get colorScheme => theme.colorScheme;
}

extension WidgetExtension on Widget {
  Widget padded([EdgeInsets padding = const EdgeInsets.all(8)]) {
    return Padding(padding: padding, child: this);
  }

  Widget centered() => Center(child: this);
}

// =============================================================================
// Top-level Functions
// =============================================================================
Widget buildLoadingWidget() {
  return const Center(child: CircularProgressIndicator());
}

Future<void> showSnackBar(BuildContext context, String message) async {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text(message)),
  );
}

// =============================================================================
// Top-level Constants
// =============================================================================
const String appName = 'FlutterDemo';
const double defaultPadding = 16.0;
const Duration animationDuration = Duration(milliseconds: 300);

final ThemeData lightTheme = ThemeData.light();
final ThemeData darkTheme = ThemeData.dark();
