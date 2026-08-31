import 'package:flutter/foundation.dart';

class AppConfig {
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://api.nuratech.ai',
  );

  static const String appEnvironment = String.fromEnvironment(
    'APP_ENVIRONMENT',
    defaultValue: 'production',
  );

  static const String privacyPolicyUrl = String.fromEnvironment(
    'PRIVACY_POLICY_URL',
    defaultValue: 'https://nuratech.ai/privacy',
  );

  static const String termsUrl = String.fromEnvironment(
    'TERMS_URL',
    defaultValue: 'https://nuratech.ai/terms',
  );

  static const String supportUrl = String.fromEnvironment(
    'SUPPORT_URL',
    defaultValue: 'https://nuratech.ai/support',
  );

  static void validate() {
    final uri = Uri.tryParse(apiBaseUrl);
    if (uri == null || !uri.hasScheme || uri.host.isEmpty) {
      throw StateError('API_BASE_URL must be an absolute URL.');
    }
    if (kReleaseMode && uri.scheme.toLowerCase() != 'https') {
      throw StateError('Release builds require an HTTPS API_BASE_URL.');
    }
    if (kReleaseMode &&
        (uri.host == '127.0.0.1' || uri.host == 'localhost')) {
      throw StateError('Release builds cannot use a loopback API host.');
    }
  }

  static Uri endpoint(String path) {
    final normalizedBase = apiBaseUrl.endsWith('/')
        ? apiBaseUrl.substring(0, apiBaseUrl.length - 1)
        : apiBaseUrl;
    final normalizedPath = path.startsWith('/') ? path : '/$path';
    return Uri.parse('$normalizedBase$normalizedPath');
  }
}
