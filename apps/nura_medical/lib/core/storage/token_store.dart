import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class StoredSession {
  const StoredSession({
    required this.accessToken,
    required this.refreshToken,
    required this.userJson,
  });

  final String accessToken;
  final String refreshToken;
  final Map<String, dynamic> userJson;
}

class TokenStore {
  TokenStore({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage();

  static const _accessKey = 'nura_access_token';
  static const _refreshKey = 'nura_refresh_token';
  static const _userKey = 'nura_user_json';
  final FlutterSecureStorage _storage;

  Future<void> save({
    required String accessToken,
    required String refreshToken,
    required Map<String, dynamic> userJson,
  }) async {
    await Future.wait([
      _storage.write(key: _accessKey, value: accessToken),
      _storage.write(key: _refreshKey, value: refreshToken),
      _storage.write(key: _userKey, value: jsonEncode(userJson)),
    ]);
  }

  Future<StoredSession?> read() async {
    final values = await Future.wait([
      _storage.read(key: _accessKey),
      _storage.read(key: _refreshKey),
      _storage.read(key: _userKey),
    ]);
    final accessToken = values[0];
    final refreshToken = values[1];
    final userValue = values[2];
    if (accessToken == null || refreshToken == null || userValue == null) {
      return null;
    }
    try {
      final decoded = jsonDecode(userValue);
      if (decoded is! Map<String, dynamic>) return null;
      return StoredSession(
        accessToken: accessToken,
        refreshToken: refreshToken,
        userJson: decoded,
      );
    } catch (_) {
      await clear();
      return null;
    }
  }

  Future<String?> accessToken() => _storage.read(key: _accessKey);
  Future<String?> refreshToken() => _storage.read(key: _refreshKey);

  Future<void> clear() async {
    await Future.wait([
      _storage.delete(key: _accessKey),
      _storage.delete(key: _refreshKey),
      _storage.delete(key: _userKey),
    ]);
  }
}
