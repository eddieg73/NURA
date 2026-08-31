import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:brawlerz_box/core/api/api_client.dart';
import 'package:brawlerz_box/shared/models/user_metrics.dart';

abstract class IUserMetricsRepository {
  Future<UserMetrics> getUserMetrics();
}

class UserMetricsRepository implements IUserMetricsRepository {
  final ApiClient _api;

  UserMetricsRepository(this._api);

  @override
  Future<UserMetrics> getUserMetrics() async {
    final payload = await _api.request('GET', '/api/v1/metrics')
        as Map<String, dynamic>;
    return UserMetrics.fromJson(payload);
  }
}

final userMetricsRepositoryProvider = Provider<IUserMetricsRepository>((ref) {
  return UserMetricsRepository(ref.watch(apiClientProvider));
});

final userMetricsProvider = FutureProvider<UserMetrics>((ref) {
  return ref.watch(userMetricsRepositoryProvider).getUserMetrics();
});
