import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:brawlerz_box/core/api/api_client.dart';

class AuthRepository {
  final ApiClient _api;

  AuthRepository(this._api);

  Future<void> login({required String email, required String password}) async {
    await _api.login(email, password);
  }

  Future<void> register({
    required String email,
    required String password,
    required String displayName,
  }) async {
    await _api.register(
      email: email,
      password: password,
      displayName: displayName,
    );
  }

  Future<Map<String, dynamic>> currentUser() async {
    return await _api.request('GET', '/api/v1/auth/me')
        as Map<String, dynamic>;
  }

  Future<bool> hasSession() => _api.hasSession();

  Future<void> logout() => _api.logout();
}

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.watch(apiClientProvider));
});

final currentUserProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  return ref.watch(authRepositoryProvider).currentUser();
});
