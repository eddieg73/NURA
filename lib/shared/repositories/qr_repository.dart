import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:brawlerz_box/core/api/api_client.dart';

class QrPass {
  final String token;
  final String memberId;
  final DateTime expiresAt;

  const QrPass({
    required this.token,
    required this.memberId,
    required this.expiresAt,
  });

  factory QrPass.fromJson(Map<String, dynamic> json) {
    return QrPass(
      token: json['token'] as String,
      memberId: json['memberId'].toString(),
      expiresAt: DateTime.parse(json['expiresAt'] as String),
    );
  }
}

class QrRepository {
  final ApiClient _api;

  QrRepository(this._api);

  Future<QrPass> createPass({int ttlMinutes = 10}) async {
    final payload = await _api.request(
      'POST',
      '/api/v1/qr/pass',
      body: {'ttlMinutes': ttlMinutes},
    ) as Map<String, dynamic>;
    return QrPass.fromJson(payload);
  }

  Future<List<DateTime>> history() async {
    final payload = await _api.request('GET', '/api/v1/qr/history') as List;
    return payload
        .whereType<Map>()
        .map((item) => DateTime.parse(item['checkedInAt'] as String))
        .toList(growable: false);
  }
}

final qrRepositoryProvider = Provider<QrRepository>((ref) {
  return QrRepository(ref.watch(apiClientProvider));
});

final qrPassProvider = FutureProvider.autoDispose<QrPass>((ref) {
  return ref.watch(qrRepositoryProvider).createPass();
});

final qrHistoryProvider = FutureProvider<List<DateTime>>((ref) {
  return ref.watch(qrRepositoryProvider).history();
});
