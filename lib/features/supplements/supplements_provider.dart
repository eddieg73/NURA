import 'package:flutter_riverpod/flutter_riverpod.dart';

final cartProvider = StateNotifierProvider<CartNotifier, Map<String, int>>((ref) {
  return CartNotifier();
});

class CartNotifier extends StateNotifier<Map<String, int>> {
  CartNotifier() : super({});

  void addToCart(String productId) {
    state = {
      ...state,
      productId: (state[productId] ?? 0) + 1,
    };
  }

  int get totalItems => state.values.fold(0, (sum, count) => sum + count);
}
