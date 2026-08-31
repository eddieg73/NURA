import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:brawlerz_box/core/api/api_client.dart';

class CartRepository {
  final ApiClient _api;

  CartRepository(this._api);

  Future<Map<String, dynamic>> getCart() async {
    return await _api.request('GET', '/api/v1/cart')
        as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> setQuantity(
    String supplementId,
    int quantity,
  ) async {
    return await _api.request(
      'PUT',
      '/api/v1/cart/$supplementId',
      body: {'quantity': quantity},
    ) as Map<String, dynamic>;
  }
}

final cartRepositoryProvider = Provider<CartRepository>((ref) {
  return CartRepository(ref.watch(apiClientProvider));
});

final remoteCartProvider = FutureProvider<Map<String, dynamic>>((ref) {
  return ref.watch(cartRepositoryProvider).getCart();
});
