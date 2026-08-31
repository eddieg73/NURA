import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:uuid/uuid.dart';

import '../config/app_config.dart';
import '../models/models.dart';
import '../storage/token_store.dart';

class ApiException implements Exception {
  const ApiException(
    this.message, {
    this.statusCode,
    this.requestId,
    this.code,
  });

  final String message;
  final int? statusCode;
  final String? requestId;
  final String? code;

  @override
  String toString() => message;
}

class ApiClient {
  ApiClient({
    required TokenStore tokenStore,
    http.Client? httpClient,
    Duration timeout = const Duration(seconds: 45),
  })  : _tokenStore = tokenStore,
        _http = httpClient ?? http.Client(),
        _timeout = timeout;

  final TokenStore _tokenStore;
  final http.Client _http;
  final Duration _timeout;
  final Uuid _uuid = const Uuid();

  Future<SessionData>? _refreshOperation;

  Future<dynamic> get(
    String path, {
    bool authenticated = true,
    Map<String, String>? headers,
  }) =>
      _request(
        'GET',
        path,
        authenticated: authenticated,
        headers: headers,
      );

  Future<dynamic> post(
    String path, {
    Map<String, dynamic>? body,
    bool authenticated = true,
    Map<String, String>? headers,
  }) =>
      _request(
        'POST',
        path,
        body: body,
        authenticated: authenticated,
        headers: headers,
      );

  Future<dynamic> patch(
    String path, {
    Map<String, dynamic>? body,
    bool authenticated = true,
    Map<String, String>? headers,
  }) =>
      _request(
        'PATCH',
        path,
        body: body,
        authenticated: authenticated,
        headers: headers,
      );

  Future<dynamic> delete(
    String path, {
    Map<String, dynamic>? body,
    bool authenticated = true,
    Map<String, String>? headers,
  }) =>
      _request(
        'DELETE',
        path,
        body: body,
        authenticated: authenticated,
        headers: headers,
      );

  Future<dynamic> _request(
    String method,
    String path, {
    Map<String, dynamic>? body,
    required bool authenticated,
    Map<String, String>? headers,
    bool allowRefresh = true,
  }) async {
    final request = http.Request(method, AppConfig.endpoint(path));
    request.headers.addAll(<String, String>{
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'X-Request-ID': _uuid.v4(),
      ...?headers,
    });

    if (authenticated) {
      final accessToken = await _tokenStore.accessToken();
      if (accessToken != null && accessToken.isNotEmpty) {
        request.headers['Authorization'] = 'Bearer $accessToken';
      }
    }

    if (body != null) {
      request.body = jsonEncode(body);
    }

    http.Response response;
    try {
      final streamed = await _http.send(request).timeout(_timeout);
      response = await http.Response.fromStream(streamed).timeout(_timeout);
    } on TimeoutException {
      throw const ApiException(
        'The NURA service did not respond in time. No clinical action was completed.',
        code: 'request_timeout',
      );
    } on http.ClientException {
      throw const ApiException(
        'The NURA service is unavailable. Check the secure connection and try again.',
        code: 'network_unavailable',
      );
    }

    if (response.statusCode == 401 && authenticated && allowRefresh) {
      final refreshed = await _refreshSession();
      if (refreshed != null) {
        return _request(
          method,
          path,
          body: body,
          authenticated: true,
          headers: headers,
          allowRefresh: false,
        );
      }
    }

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw _errorFromResponse(response);
    }

    if (response.statusCode == 204 || response.body.trim().isEmpty) {
      return null;
    }

    try {
      return jsonDecode(response.body);
    } on FormatException {
      throw ApiException(
        'The NURA service returned an invalid response.',
        statusCode: response.statusCode,
        requestId: response.headers['x-request-id'],
        code: 'invalid_response',
      );
    }
  }

  Future<SessionData?> _refreshSession() async {
    final active = _refreshOperation;
    if (active != null) {
      try {
        return await active;
      } catch (_) {
        return null;
      }
    }

    final refreshToken = await _tokenStore.refreshToken();
    if (refreshToken == null || refreshToken.isEmpty) {
      await _tokenStore.clear();
      return null;
    }

    final operation = _performRefresh(refreshToken);
    _refreshOperation = operation;
    try {
      return await operation;
    } catch (_) {
      await _tokenStore.clear();
      return null;
    } finally {
      _refreshOperation = null;
    }
  }

  Future<SessionData> _performRefresh(String refreshToken) async {
    final response = await _request(
      'POST',
      '/api/v1/auth/refresh',
      authenticated: false,
      allowRefresh: false,
      body: <String, dynamic>{
        'refresh_token': refreshToken,
        'device_label': 'NURA Medical iOS',
      },
    );
    if (response is! Map<String, dynamic>) {
      throw const ApiException(
        'The session refresh response was invalid.',
        code: 'invalid_refresh_response',
      );
    }
    final session = SessionData.fromJson(response);
    await _tokenStore.save(
      accessToken: session.accessToken,
      refreshToken: session.refreshToken,
      userJson: session.user.toJson(),
    );
    return session;
  }

  ApiException _errorFromResponse(http.Response response) {
    final requestId = response.headers['x-request-id'];
    String? code;
    String message = 'The NURA service could not complete the request.';

    try {
      final decoded = jsonDecode(response.body);
      if (decoded is Map) {
        final detail = decoded['detail'] ?? decoded['error'];
        if (detail is String && detail.trim().isNotEmpty) {
          code = detail;
          message = _friendlyMessage(detail);
        } else if (detail is List && detail.isNotEmpty) {
          code = 'validation_error';
          message = 'Review the submitted information and try again.';
        }
      }
    } on FormatException {
      // Preserve a safe generic message rather than exposing upstream content.
    }

    return ApiException(
      message,
      statusCode: response.statusCode,
      requestId: requestId,
      code: code,
    );
  }

  String _friendlyMessage(String code) {
    const messages = <String, String>{
      'invalid_credentials': 'The email or password is incorrect.',
      'inactive_user': 'This account is inactive.',
      'invalid_access_token': 'Your secure session has expired. Sign in again.',
      'invalid_refresh_token': 'Your secure session has expired. Sign in again.',
      'refresh_token_expired': 'Your secure session has expired. Sign in again.',
      'consent_attestation_required':
          'Document the required consent before creating a scribe draft.',
      'clinical_engine_not_configured':
          'Clinical draft generation is not configured in this environment.',
      'clinical_engine_unavailable':
          'The clinical draft service is temporarily unavailable.',
      'resource_not_found': 'The requested record is unavailable.',
      'self_registration_disabled':
          'Account creation is managed by your organization.',
      'invalid_password': 'The password could not be verified.',
    };
    return messages[code] ?? code.replaceAll('_', ' ');
  }

  void close() => _http.close();
}
