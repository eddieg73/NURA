import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:uuid/uuid.dart';

import '../config/app_config.dart';
import '../storage/token_store.dart';

class ApiException implements Exception {
  const ApiException(this.message, {this.statusCode, this.requestId});

  final String message;
  final int? statusCode;
  final String? requestId;

  @override
  String toString() => message;
}

class ApiClient {
  ApiClient({required TokenStore tokenStore, http.Client? client})
      : _tokenStore = tokenStore,
        _client = client ?? http.Client();

  final TokenStore _tokenStore;
  final http.Client _client;
  final Uuid _uuid = const Uuid();
  Future<bool>? _refreshInFlight;

  Future<dynamic> get(String path, {bool authenticated = true}) =>
      request('GET', path, authenticated: authenticated);

  Future<dynamic> post(
    String path, {
    Map<String, dynamic>? body,
    bool authenticated = true,
  }) =>
      request('POST', path, body: body, authenticated: authenticated);

  Future<dynamic> patch(
    String path, {
    Map<String, dynamic>? body,
    bool authenticated = true,
  }) =>
      request('PATCH', path, body: body, authenticated: authenticated);

  Future<dynamic> delete(
    String path, {
    Map<String, dynamic>? body,
    bool authenticated = true,
  }) =>
      request('DELETE', path, body: body, authenticated: authenticated);

  Future<dynamic> request(
    String method,
    String path, {
    Map<String, dynamic>? body,
    bool authenticated = true,
    bool retryAfterRefresh = true,
  }) async {
    final response = await _send(
      method,
      path,
      body: body,
      authenticated: authenticated,
    );
    if (response.statusCode == 401 &&
        authenticated &&
        retryAfterRefresh &&
        await _refreshTokens()) {
      return request(
        method,
        path,
        body: body,
        authenticated: authenticated,
        retryAfterRefresh: false,
      );
    }
    return _decode(response);
  }

  Future<http.Response> _send(
    String method,
    String path, {
    Map<String, dynamic>? body,
    required bool authenticated,
  }) async {
    final request = http.Request(method, AppConfig.endpoint(path));
    request.headers['Accept'] = 'application/json';
    request.headers['Content-Type'] = 'application/json';
    request.headers['X-Request-ID'] = _uuid.v4();
    if (authenticated) {
      final token = await _tokenStore.accessToken();
      if (token == null) {
        throw const ApiException('Your session has expired. Please sign in again.');
      }
      request.headers['Authorization'] = 'Bearer $token';
    }
    if (body != null) request.body = jsonEncode(body);
    try {
      final streamed = await _client.send(request).timeout(
            const Duration(seconds: 50),
          );
      return http.Response.fromStream(streamed);
    } catch (_) {
      throw const ApiException(
        'The NURA service could not be reached. Check your secure connection and try again.',
      );
    }
  }

  dynamic _decode(http.Response response) {
    final requestId = response.headers['x-request-id'];
    dynamic decoded;
    if (response.body.isNotEmpty) {
      try {
        decoded = jsonDecode(response.body);
      } catch (_) {
        decoded = response.body;
      }
    }
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return decoded;
    }
    String message = 'Request failed (${response.statusCode}).';
    if (decoded is Map<String, dynamic>) {
      final detail = decoded['detail'];
      if (detail is String) message = _friendlyMessage(detail);
    }
    throw ApiException(
      message,
      statusCode: response.statusCode,
      requestId: requestId,
    );
  }

  Future<bool> _refreshTokens() async {
    final existing = _refreshInFlight;
    if (existing != null) return existing;
    final future = _performRefresh();
    _refreshInFlight = future;
    try {
      return await future;
    } finally {
      _refreshInFlight = null;
    }
  }

  Future<bool> _performRefresh() async {
    final refreshToken = await _tokenStore.refreshToken();
    if (refreshToken == null) return false;
    try {
      final response = await _send(
        'POST',
        '/api/v1/auth/refresh',
        body: {
          'refresh_token': refreshToken,
          'device_label': 'nura-medical-flutter',
        },
        authenticated: false,
      );
      final decoded = _decode(response);
      if (decoded is! Map<String, dynamic>) return false;
      final user = decoded['user'];
      if (user is! Map<String, dynamic>) return false;
      await _tokenStore.save(
        accessToken: decoded['access_token'] as String,
        refreshToken: decoded['refresh_token'] as String,
        userJson: user,
      );
      return true;
    } catch (_) {
      await _tokenStore.clear();
      return false;
    }
  }

  static String _friendlyMessage(String detail) {
    const messages = {
      'invalid_credentials': 'The email or password is incorrect.',
      'self_registration_disabled':
          'Account creation is managed by your NURA administrator.',
      'consent_attestation_required':
          'Confirm patient consent and your authority before submitting clinical text.',
      'clinical_provider_unavailable':
          'The approved clinical drafting service is unavailable. No draft was generated.',
      'insufficient_role': 'Your account is not authorized for that action.',
      'draft_not_found': 'The clinical draft was not found.',
      'task_not_found': 'The task was not found.',
      'inactive_user': 'This account is inactive.',
      'stale_access_token': 'Your access changed. Sign in again.',
    };
    return messages[detail] ?? detail.replaceAll('_', ' ');
  }

  void close() => _client.close();
}
