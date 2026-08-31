import '../models/models.dart';
import '../network/api_client.dart';
import '../storage/token_store.dart';

class AuthRepository {
  AuthRepository(this._api, this._tokens);

  final ApiClient _api;
  final TokenStore _tokens;

  Future<AppUser?> restoreSession() async {
    final stored = await _tokens.read();
    if (stored == null) return null;
    try {
      final response = await _api.get('/api/v1/account/me');
      if (response is Map<String, dynamic>) {
        return AppUser.fromJson(response);
      }
      return AppUser.fromJson(stored.userJson);
    } on ApiException catch (error) {
      if (error.statusCode == 401) {
        await _tokens.clear();
        return null;
      }
      return AppUser.fromJson(stored.userJson);
    }
  }

  Future<AppUser> login(String email, String password) async {
    final response = await _api.post(
      '/api/v1/auth/login',
      authenticated: false,
      body: {
        'email': email.trim().toLowerCase(),
        'password': password,
        'device_label': 'NURA Medical iOS',
      },
    );
    if (response is! Map<String, dynamic>) {
      throw const ApiException('The sign-in response was invalid.');
    }
    final session = SessionData.fromJson(response);
    await _tokens.save(
      accessToken: session.accessToken,
      refreshToken: session.refreshToken,
      userJson: session.user.toJson(),
    );
    return session.user;
  }

  Future<void> logout() async {
    final refreshToken = await _tokens.refreshToken();
    try {
      if (refreshToken != null) {
        await _api.post(
          '/api/v1/auth/logout',
          authenticated: false,
          body: {'refresh_token': refreshToken},
        );
      }
    } finally {
      await _tokens.clear();
    }
  }

  Future<Map<String, dynamic>> exportAccount() async {
    final response = await _api.get('/api/v1/account/export');
    if (response is! Map<String, dynamic>) {
      throw const ApiException('The account export was invalid.');
    }
    return response;
  }

  Future<void> deleteAccount(String password) async {
    await _api.delete(
      '/api/v1/account',
      body: {'password': password, 'confirmation': 'DELETE'},
    );
    await _tokens.clear();
  }
}

class ClinicalRepository {
  const ClinicalRepository(this._api);

  final ApiClient _api;

  Future<ClinicalDraft> createDraft({
    required String operation,
    required String caseText,
    required bool consentAttested,
    String? patientReference,
  }) async {
    final response = await _api.post(
      '/api/v1/clinical/drafts',
      body: {
        'operation': operation,
        'case_text': caseText,
        'patient_reference': patientReference?.trim().isEmpty == true
            ? null
            : patientReference?.trim(),
        'consent_attested': consentAttested,
      },
    );
    if (response is! Map<String, dynamic>) {
      throw const ApiException('The clinical draft response was invalid.');
    }
    return ClinicalDraft.fromJson(response);
  }

  Future<List<ClinicalDraft>> listDrafts() async {
    final response = await _api.get('/api/v1/clinical/drafts');
    if (response is! List) return const [];
    return response
        .whereType<Map>()
        .map((item) => ClinicalDraft.fromJson(
              Map<String, dynamic>.from(item),
            ))
        .toList(growable: false);
  }

  Future<ClinicalDraft> review({
    required String draftId,
    required String status,
    String? comment,
  }) async {
    final response = await _api.post(
      '/api/v1/clinical/drafts/$draftId/review',
      body: {
        'status': status,
        'comment': comment?.trim().isEmpty == true ? null : comment?.trim(),
      },
    );
    if (response is! Map<String, dynamic>) {
      throw const ApiException('The clinical review response was invalid.');
    }
    return ClinicalDraft.fromJson(response);
  }
}

class OpsRepository {
  const OpsRepository(this._api);

  final ApiClient _api;

  Future<List<OpsTask>> listTasks() async {
    final response = await _api.get('/api/v1/ops/tasks');
    if (response is! List) return const [];
    return response
        .whereType<Map>()
        .map((item) => OpsTask.fromJson(Map<String, dynamic>.from(item)))
        .toList(growable: false);
  }

  Future<OpsTask> createTask({
    required String title,
    String? detail,
    String priority = 'normal',
  }) async {
    final response = await _api.post(
      '/api/v1/ops/tasks',
      body: {
        'title': title,
        'detail': detail,
        'priority': priority,
      },
    );
    if (response is! Map<String, dynamic>) {
      throw const ApiException('The task response was invalid.');
    }
    return OpsTask.fromJson(response);
  }

  Future<OpsTask> setStatus(String taskId, String status) async {
    final response = await _api.patch(
      '/api/v1/ops/tasks/$taskId',
      body: {'status': status},
    );
    if (response is! Map<String, dynamic>) {
      throw const ApiException('The task response was invalid.');
    }
    return OpsTask.fromJson(response);
  }
}

class LegalRepository {
  const LegalRepository(this._api);

  final ApiClient _api;

  Future<LegalConfig> load() async {
    final response = await _api.get('/api/v1/legal', authenticated: false);
    if (response is! Map<String, dynamic>) {
      throw const ApiException('The legal configuration was invalid.');
    }
    return LegalConfig.fromJson(response);
  }
}
