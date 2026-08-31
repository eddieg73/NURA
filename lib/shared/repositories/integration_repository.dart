import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:brawlerz_box/core/api/api_client.dart';

class IntegrationConnectionModel {
  final String provider;
  final bool connected;

  const IntegrationConnectionModel({
    required this.provider,
    required this.connected,
  });

  factory IntegrationConnectionModel.fromJson(Map<String, dynamic> json) {
    return IntegrationConnectionModel(
      provider: json['provider'] as String? ?? '',
      connected: json['connected'] as bool? ?? false,
    );
  }
}

class IntegrationRepository {
  final ApiClient _api;

  IntegrationRepository(this._api);

  Future<List<IntegrationConnectionModel>> list() async {
    final payload = await _api.request('GET', '/api/v1/integrations') as List;
    return payload
        .whereType<Map>()
        .map((item) => IntegrationConnectionModel.fromJson(
              Map<String, dynamic>.from(item),
            ))
        .toList(growable: false);
  }

  Future<IntegrationConnectionModel> setConnected(
    String provider,
    bool connected,
  ) async {
    final payload = await _api.request(
      'PUT',
      '/api/v1/integrations/$provider',
      body: {'connected': connected},
    ) as Map<String, dynamic>;
    return IntegrationConnectionModel.fromJson(payload);
  }
}

final integrationRepositoryProvider = Provider<IntegrationRepository>((ref) {
  return IntegrationRepository(ref.watch(apiClientProvider));
});

final integrationsProvider =
    FutureProvider<List<IntegrationConnectionModel>>((ref) {
  return ref.watch(integrationRepositoryProvider).list();
});
