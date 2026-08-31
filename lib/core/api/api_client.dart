import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'package:brawlerz_box/core/api/token_store.dart';

class ApiException implements Exception {
  final int statusCode;
  final String message;

  const ApiException(this.statusCode, this.message);

  @override
  String toString() => message;
}

class ApiClient {
  static const configuredBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8080',
  );

  final http.Client _http;
  final TokenStore _tokens;
  final String _baseUrl;
  Future<bool>? _refreshInFlight;

  ApiClient({
    http.Client? httpClient,
    TokenStore? tokenStore,
    String baseUrl = configuredBaseUrl,
  })  : _http = httpClient ?? http.Client(),
        _tokens = tokenStore ?? const TokenStore(),
        _baseUrl = baseUrl.endsWith('/')
            ? baseUrl.substring(0, baseUrl.length - 1)
            : baseUrl;

  Future<Map<String, dynamic>> login(String email, String password) async {
    final payload = await request(
      'POST',
      '/api/v1/auth/login',
      body: {'email': email.trim(), 'password': password},
      authenticated: false,
    ) as Map<String, dynamic>;
    await _storeTokenPayload(payload);
    return payload;
  }

  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String displayName,
  }) async {
    final payload = await request(
      'POST',
      '/api/v1/auth/register',
      body: {
        'email': email.trim(),
        'password': password,
        'displayName': displayName.trim(),
      },
      authenticated: false,
    ) as Map<String, dynamic>;
    await _storeTokenPayload(payload);
    return payload;
  }

  Future<bool> hasSession() async {
    final accessToken = await _tokens.readAccessToken();
    final refreshToken = await _tokens.readRefreshToken();
    return accessToken != null || refreshToken != null;
  }

  Future<void> logout() async {
    final refreshToken = await _tokens.readRefreshToken();
    if (refreshToken != null) {
      try {
        await request(
          'POST',
          '/api/v1/auth/logout',
          body: {'refreshToken': refreshToken},
          authenticated: false,
        );
      } catch (_) {
        // Local logout must still complete when the network is unavailable.
      }
    }
    await _tokens.clear();
  }

  Future<dynamic> request(
    String method,
    String path, {
    Map<String, dynamic>? body,
    bool authenticated = true,
    bool retryOnUnauthorized = true,
  }) async {
    final headers = <String, String>{
      'Accept': 'application/json',
      if (body != null) 'Content-Type': 'application/json',
    };
    if (authenticated) {
      final token = await _tokens.readAccessToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }

    final response = await _send(
      method,
      Uri.parse('$_baseUrl$path'),
      headers,
      body,
    );

    if (response.statusCode == 401 && authenticated && retryOnUnauthorized) {
      final refreshed = await _refreshAccessToken();
      if (refreshed) {
        return request(
          method,
          path,
          body: body,
          authenticated: authenticated,
          retryOnUnauthorized: false,
        );
      }
    }

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException(
        response.statusCode,
        _errorMessage(response),
      );
    }
    if (response.statusCode == 204 || response.bodyBytes.isEmpty) {
      return null;
    }
    return jsonDecode(utf8.decode(response.bodyBytes));
  }

  Future<http.Response> _send(
    String method,
    Uri uri,
    Map<String, String> headers,
    Map<String, dynamic>? body,
  ) {
    final encoded = body == null ? null : jsonEncode(body);
    switch (method.toUpperCase()) {
      case 'GET':
        return _http.get(uri, headers: headers);
      case 'POST':
        return _http.post(uri, headers: headers, body: encoded);
      case 'PUT':
        return _http.put(uri, headers: headers, body: encoded);
      case 'PATCH':
        return _http.patch(uri, headers: headers, body: encoded);
      case 'DELETE':
        return _http.delete(uri, headers: headers, body: encoded);
      default:
        throw ArgumentError.value(method, 'method', 'Unsupported HTTP method');
    }
  }

  Future<bool> _refreshAccessToken() async {
    final existing = _refreshInFlight;
    if (existing != null) {
      return existing;
    }
    final future = _performRefresh();
    _refreshInFlight = future;
    try {
      return await future;
    } finally {
      _refreshInFlight = null;
    }
  }

  Future<bool> _performRefresh() async {
    final refreshToken = await _tokens.readRefreshToken();
    if (refreshToken == null) {
      await _tokens.clear();
      return false;
    }
    try {
      final payload = await request(
        'POST',
        '/api/v1/auth/refresh',
        body: {'refreshToken': refreshToken},
        authenticated: false,
        retryOnUnauthorized: false,
      ) as Map<String, dynamic>;
      await _storeTokenPayload(payload);
      return true;
    } catch (_) {
      await _tokens.clear();
      return false;
    }
  }

  Future<void> _storeTokenPayload(Map<String, dynamic> payload) async {
    final accessToken = payload['accessToken'] as String?;
    final refreshToken = payload['refreshToken'] as String?;
    if (accessToken == null || refreshToken == null) {
      throw const ApiException(500, 'The server returned an invalid token response.');
    }
    await _tokens.saveTokens(
      accessToken: accessToken,
      refreshToken: refreshToken,
    );
  }

  String _errorMessage(http.Response response) {
    try {
      final decoded = jsonDecode(utf8.decode(response.bodyBytes));
      if (decoded is Map<String, dynamic>) {
        final detail = decoded['detail'];
        if (detail is String && detail.isNotEmpty) {
          return detail.replaceAll('_', ' ');
        }
      }
    } catch (_) {
      // Fall through to the generic HTTP error.
    }
    return 'Request failed (${response.statusCode}).';
  }

  void close() => _http.close();
}

final tokenStoreProvider = Provider<TokenStore>((ref) => const TokenStore());

final apiClientProvider = Provider<ApiClient>((ref) {
  final client = ApiClient(tokenStore: ref.watch(tokenStoreProvider));
  ref.onDispose(client.close);
  return client;
});
