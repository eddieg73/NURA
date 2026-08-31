import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'models/models.dart';
import 'network/api_client.dart';
import 'repositories/repositories.dart';
import 'storage/token_store.dart';

final tokenStoreProvider = Provider<TokenStore>((ref) => TokenStore());

final apiClientProvider = Provider<ApiClient>((ref) {
  final client = ApiClient(tokenStore: ref.watch(tokenStoreProvider));
  ref.onDispose(client.close);
  return client;
});

final authRepositoryProvider = Provider<AuthRepository>((ref) => AuthRepository(
      ref.watch(apiClientProvider),
      ref.watch(tokenStoreProvider),
    ));

final clinicalRepositoryProvider = Provider<ClinicalRepository>(
  (ref) => ClinicalRepository(ref.watch(apiClientProvider)),
);

final opsRepositoryProvider = Provider<OpsRepository>(
  (ref) => OpsRepository(ref.watch(apiClientProvider)),
);

final legalRepositoryProvider = Provider<LegalRepository>(
  (ref) => LegalRepository(ref.watch(apiClientProvider)),
);

class AuthState {
  const AuthState({
    required this.loading,
    this.user,
    this.error,
  });

  const AuthState.loading() : this(loading: true);

  final bool loading;
  final AppUser? user;
  final String? error;

  AuthState copyWith({
    bool? loading,
    AppUser? user,
    bool clearUser = false,
    String? error,
    bool clearError = false,
  }) =>
      AuthState(
        loading: loading ?? this.loading,
        user: clearUser ? null : (user ?? this.user),
        error: clearError ? null : (error ?? this.error),
      );
}

class AuthController extends StateNotifier<AuthState> {
  AuthController(this._repository) : super(const AuthState.loading()) {
    restore();
  }

  final AuthRepository _repository;

  Future<void> restore() async {
    state = const AuthState.loading();
    try {
      final user = await _repository.restoreSession();
      state = AuthState(loading: false, user: user);
    } catch (error) {
      state = AuthState(loading: false, error: error.toString());
    }
  }

  Future<bool> login(String email, String password) async {
    state = state.copyWith(loading: true, clearError: true);
    try {
      final user = await _repository.login(email, password);
      state = AuthState(loading: false, user: user);
      return true;
    } catch (error) {
      state = AuthState(
        loading: false,
        error: error.toString(),
      );
      return false;
    }
  }

  Future<void> logout() async {
    state = state.copyWith(loading: true, clearError: true);
    try {
      await _repository.logout();
    } finally {
      state = const AuthState(loading: false);
    }
  }

  Future<bool> deleteAccount(String password) async {
    state = state.copyWith(loading: true, clearError: true);
    try {
      await _repository.deleteAccount(password);
      state = const AuthState(loading: false);
      return true;
    } catch (error) {
      state = AuthState(
        loading: false,
        user: state.user,
        error: error.toString(),
      );
      return false;
    }
  }

  void clearError() => state = state.copyWith(clearError: true);
}

final authControllerProvider =
    StateNotifierProvider<AuthController, AuthState>((ref) {
  return AuthController(ref.watch(authRepositoryProvider));
});
