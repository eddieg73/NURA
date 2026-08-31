import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:brawlerz_box/core/api/api_client.dart';
import 'package:brawlerz_box/shared/models/supplement.dart';

abstract class ISupplementRepository {
  Future<List<Supplement>> getSupplements();
}

class SupplementRepository implements ISupplementRepository {
  final ApiClient _api;

  SupplementRepository(this._api);

  @override
  Future<List<Supplement>> getSupplements() async {
    final payload = await _api.request('GET', '/api/v1/supplements') as List;
    return payload
        .whereType<Map>()
        .map((item) => Supplement.fromJson(
              Map<String, dynamic>.from(item),
            ))
        .toList(growable: false);
  }
}

final supplementRepositoryProvider = Provider<ISupplementRepository>((ref) {
  return SupplementRepository(ref.watch(apiClientProvider));
});

final supplementsProvider = FutureProvider<List<Supplement>>((ref) {
  return ref.watch(supplementRepositoryProvider).getSupplements();
});
