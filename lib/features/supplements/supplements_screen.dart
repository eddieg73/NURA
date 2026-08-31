import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:brawlerz_box/core/api/api_client.dart';
import 'package:brawlerz_box/shared/models/supplement.dart';
import 'package:brawlerz_box/shared/repositories/cart_repository.dart';
import 'package:brawlerz_box/shared/repositories/supplement_repository.dart';
import 'package:brawlerz_box/shared/widgets/async_content.dart';
import 'package:brawlerz_box/shared/widgets/brawlerz_card.dart';

class SupplementsScreen extends ConsumerStatefulWidget {
  const SupplementsScreen({super.key});

  @override
  ConsumerState<SupplementsScreen> createState() => _SupplementsScreenState();
}

class _SupplementsScreenState extends ConsumerState<SupplementsScreen> {
  final Set<String> _busy = {};

  int _quantityFor(Map<String, dynamic>? cart, String productId) {
    final items = cart?['items'];
    if (items is! List) return 0;
    for (final item in items.whereType<Map>()) {
      final product = item['supplement'];
      if (product is Map && product['id'].toString() == productId) {
        return (item['quantity'] as num?)?.toInt() ?? 0;
      }
    }
    return 0;
  }

  int _cartCount(Map<String, dynamic>? cart) {
    final items = cart?['items'];
    if (items is! List) return 0;
    return items.whereType<Map>().fold<int>(
          0,
          (sum, item) => sum + ((item['quantity'] as num?)?.toInt() ?? 0),
        );
  }

  Future<void> _addToCart(
    Supplement product,
    Map<String, dynamic>? cart,
  ) async {
    if (_busy.contains(product.id) || !product.inStock) return;
    setState(() => _busy.add(product.id));
    try {
      final quantity = _quantityFor(cart, product.id) + 1;
      await ref.read(cartRepositoryProvider).setQuantity(product.id, quantity);
      ref.invalidate(remoteCartProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${product.name} added to your cart.')),
        );
      }
    } on ApiException catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(error.message), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _busy.remove(product.id));
    }
  }

  @override
  Widget build(BuildContext context) {
    final products = ref.watch(supplementsProvider);
    final cart = ref.watch(remoteCartProvider);
    final cartData = cart.asData?.value;
    final cartCount = _cartCount(cartData);

    return Scaffold(
      appBar: AppBar(
        title: Text(
          'STORE',
          style: GoogleFonts.oswald(fontWeight: FontWeight.bold),
        ),
        actions: [
          Stack(
            alignment: Alignment.center,
            children: [
              IconButton(
                icon: const Icon(Icons.shopping_cart_outlined),
                onPressed: () {},
              ),
              if (cartCount > 0)
                Positioned(
                  top: 8,
                  right: 8,
                  child: Container(
                    padding: const EdgeInsets.all(4),
                    decoration: const BoxDecoration(
                      color: Color(0xFFFF4500),
                      shape: BoxShape.circle,
                    ),
                    constraints: const BoxConstraints(
                      minWidth: 16,
                      minHeight: 16,
                    ),
                    child: Text(
                      '$cartCount',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: products.when(
        loading: () => const AsyncLoadingView(),
        error: (error, _) => AsyncErrorView(
          error: error,
          onRetry: () => ref.invalidate(supplementsProvider),
        ),
        data: (supplements) => RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(supplementsProvider);
            ref.invalidate(remoteCartProvider);
            await ref.read(supplementsProvider.future);
            await ref.read(remoteCartProvider.future);
          },
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const BrawlerzCard(
                  color: Color(0x1AFF4500),
                  child: Row(
                    children: [
                      Icon(Icons.inventory_2, color: Color(0xFFFF4500)),
                      SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          'Catalog, inventory and cart are synchronized with the backend.',
                          style: TextStyle(fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  'AVAILABLE PRODUCTS',
                  style: GoogleFonts.oswald(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.2,
                  ),
                ),
                const SizedBox(height: 16),
                GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                    childAspectRatio: 0.62,
                  ),
                  itemCount: supplements.length,
                  itemBuilder: (context, index) {
                    final product = supplements[index];
                    return _buildProductCard(context, product, cartData);
                  },
                ),
                const SizedBox(height: 40),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildProductCard(
    BuildContext context,
    Supplement product,
    Map<String, dynamic>? cart,
  ) {
    final busy = _busy.contains(product.id);
    return BrawlerzCard(
      padding: EdgeInsets.zero,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Stack(
              children: [
                SizedBox.expand(
                  child: product.imageUrl.isEmpty
                      ? const Icon(Icons.local_drink, size: 48)
                      : ClipRRect(
                          borderRadius: const BorderRadius.vertical(
                            top: Radius.circular(12),
                          ),
                          child: Image.network(
                            product.imageUrl,
                            fit: BoxFit.cover,
                            errorBuilder: (_, __, ___) =>
                                const Icon(Icons.local_drink, size: 48),
                          ),
                        ),
                ),
                Positioned(
                  top: 8,
                  left: 8,
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 6,
                      vertical: 2,
                    ),
                    decoration: BoxDecoration(
                      color: product.inStock ? Colors.green : Colors.red,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      product.inStock ? 'IN STOCK' : 'OUT OF STOCK',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 8,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  product.name,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  '\$${product.price.toStringAsFixed(2)}',
                  style: GoogleFonts.oswald(
                    color: const Color(0xFFFF4500),
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 8),
                if (product.tags.isNotEmpty)
                  Text(
                    product.tags.first.toUpperCase(),
                    style: TextStyle(
                      color: Colors.grey[500],
                      fontSize: 8,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size(0, 34),
                      padding: EdgeInsets.zero,
                    ),
                    onPressed: busy || !product.inStock
                        ? null
                        : () => _addToCart(product, cart),
                    child: busy
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : Text(
                            'ADD (${_quantityFor(cart, product.id)})',
                            style: const TextStyle(fontSize: 10),
                          ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
