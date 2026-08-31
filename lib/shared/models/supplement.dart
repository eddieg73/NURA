class Supplement {
  final String id;
  final String name;
  final String description;
  final double price;
  final String imageUrl;
  final List<String> tags;
  final int inventory;
  final bool inStock;

  const Supplement({
    required this.id,
    required this.name,
    required this.description,
    required this.price,
    required this.imageUrl,
    required this.tags,
    this.inventory = 0,
    this.inStock = true,
  });

  factory Supplement.fromJson(Map<String, dynamic> json) {
    final rawTags = json['tags'];
    return Supplement(
      id: json['id'].toString(),
      name: json['name'] as String? ?? '',
      description: json['description'] as String? ?? '',
      price: (json['price'] as num?)?.toDouble() ?? 0,
      imageUrl: json['imageUrl'] as String? ?? '',
      tags: rawTags is List
          ? rawTags.whereType<String>().toList(growable: false)
          : const [],
      inventory: (json['inventory'] as num?)?.toInt() ?? 0,
      inStock: json['inStock'] as bool? ?? true,
    );
  }
}
