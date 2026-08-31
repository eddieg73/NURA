import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:brawlerz_box/core/api/api_client.dart';

class AdminRepository {
  final ApiClient _api;

  AdminRepository(this._api);

  Future<Map<String, dynamic>> summary() async {
    return await _api.request('GET', '/api/v1/admin/summary')
        as Map<String, dynamic>;
  }
}

final adminRepositoryProvider = Provider<AdminRepository>((ref) {
  return AdminRepository(ref.watch(apiClientProvider));
});

final adminSummaryProvider = FutureProvider<Map<String, dynamic>>((ref) {
  return ref.watch(adminRepositoryProvider).summary();
});
