import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';

// =============================================================================
// Typedef
// =============================================================================
typedef JsonMap = Map<String, dynamic>;
typedef VoidCallback = void Function();
typedef AsyncCallback = Future<void> Function();

// =============================================================================
// Enum
// =============================================================================
enum UserStatus {
  active,
  inactive,
  pending,
  banned;

  bool get isActive => this == UserStatus.active;
}

enum HttpMethod { get, post, put, delete, patch }

// =============================================================================
// Mixin
// =============================================================================
mixin Loggable {
  void log(String message) {
    print('[LOG] $message');
  }
}

mixin Serializable on Object {
  Map<String, dynamic> toJson();
}

// =============================================================================
// Abstract Class
// =============================================================================
abstract class BaseEntity {
  final String id;
  final DateTime createdAt;

  BaseEntity({required this.id, required this.createdAt});

  void validate();
}

// =============================================================================
// Sealed Class (Dart 3.0+)
// =============================================================================
sealed class Result<T> {
  const Result();
}

final class Success<T> extends Result<T> {
  final T value;
  const Success(this.value);
}

final class Failure<T> extends Result<T> {
  final Exception error;
  const Failure(this.error);
}

// =============================================================================
// Interface Class (Dart 3.0+)
// =============================================================================
interface class UserRepository {
  Future<User?> findById(String id) async => null;
  Future<List<User>> findAll() async => [];
  Future<void> save(User user) async {}
}

// =============================================================================
// Base Class (Dart 3.0+)
// =============================================================================
base class Animal {
  final String name;
  Animal(this.name);
  
  void speak() {
    print('Animal speaks');
  }
}

// =============================================================================
// Mixin Class (Dart 3.0+)
// =============================================================================
mixin class Walker {
  void walk() {
    print('Walking...');
  }
}

// =============================================================================
// Regular Class with Mixin
// =============================================================================
class User extends BaseEntity with Loggable {
  final String username;
  final String email;
  final UserStatus status;

  User({
    required super.id,
    required super.createdAt,
    required this.username,
    required this.email,
    this.status = UserStatus.active,
  });

  // Named constructor
  User.guest()
      : username = 'guest',
        email = 'guest@example.com',
        status = UserStatus.active,
        super(id: 'guest', createdAt: DateTime.now());

  // Factory constructor
  factory User.fromJson(JsonMap json) {
    return User(
      id: json['id'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
      username: json['username'] as String,
      email: json['email'] as String,
    );
  }

  @override
  void validate() {
    if (username.isEmpty) throw Exception('Username cannot be empty');
    if (!email.contains('@')) throw Exception('Invalid email');
  }
}

// =============================================================================
// Flutter StatefulWidget
// =============================================================================
class UserProfileWidget extends StatefulWidget {
  final User user;

  const UserProfileWidget({super.key, required this.user});

  @override
  State<UserProfileWidget> createState() => _UserProfileWidgetState();
}

class _UserProfileWidgetState extends State<UserProfileWidget> {
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    await Future.delayed(const Duration(seconds: 1));
    setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Container();
  }
}

// =============================================================================
// Flutter StatelessWidget
// =============================================================================
class UserCard extends StatelessWidget {
  final User user;
  final VoidCallback? onTap;

  const UserCard({super.key, required this.user, this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Card(
        child: Text(user.username),
      ),
    );
  }
}

// =============================================================================
// Extension
// =============================================================================
extension StringExtension on String {
  String get capitalize {
    if (isEmpty) return this;
    return '${this[0].toUpperCase()}${substring(1)}';
  }

  bool get isValidEmail => contains('@') && contains('.');
}

extension ListExtension<T> on List<T> {
  T? get firstOrNull => isEmpty ? null : first;
  T? get lastOrNull => isEmpty ? null : last;
}

// Anonymous extension
extension on int {
  bool get isEven => this % 2 == 0;
}

// =============================================================================
// Extension Type (Dart 3.3+)
// =============================================================================
extension type UserId(String value) {
  factory UserId.generate() => UserId(DateTime.now().millisecondsSinceEpoch.toString());
  
  bool get isValid => value.isNotEmpty;
}

extension type Email(String value) implements String {
  bool get isValid => value.contains('@');
}

// =============================================================================
// Top-level Functions
// =============================================================================
Future<User?> fetchUser(String id) async {
  // Simulate API call
  await Future.delayed(const Duration(milliseconds: 100));
  return null;
}

Stream<int> countStream(int max) async* {
  for (int i = 0; i < max; i++) {
    yield i;
  }
}

void printMessage(String message) {
  print(message);
}

T? tryCast<T>(dynamic value) {
  return value is T ? value : null;
}

// =============================================================================
// Getter and Setter
// =============================================================================
class Configuration {
  static String _apiUrl = 'https://api.example.com';
  static int _timeout = 30;

  static String get apiUrl => _apiUrl;
  static set apiUrl(String value) => _apiUrl = value;

  static int get timeout => _timeout;
  static set timeout(int value) {
    if (value > 0) _timeout = value;
  }
}

// =============================================================================
// Top-level Constants and Variables
// =============================================================================
const String appName = 'MyFlutterApp';
const int maxRetries = 3;
const double defaultPadding = 16.0;

final DateTime appStartTime = DateTime.now();
final RegExp emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');

/* 多行注释测试
   class FakeClass 不应被识别
   void fakeFunction() 也不应被识别
*/

// class InCommentClass 不应被识别
