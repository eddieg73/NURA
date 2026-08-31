class NutritionData {
  final int dailyCalories;
  final int targetCalories;
  final double proteinGrams;
  final double proteinTarget;
  final double carbsGrams;
  final double carbsTarget;
  final double fatGrams;
  final double fatTarget;
  final List<Meal> meals;

  const NutritionData({
    required this.dailyCalories,
    required this.targetCalories,
    required this.proteinGrams,
    required this.proteinTarget,
    required this.carbsGrams,
    required this.carbsTarget,
    required this.fatGrams,
    required this.fatTarget,
    required this.meals,
  });

  factory NutritionData.fromJson(Map<String, dynamic> json) {
    final rawMeals = json['meals'];
    return NutritionData(
      dailyCalories: (json['dailyCalories'] as num?)?.toInt() ?? 0,
      targetCalories: (json['targetCalories'] as num?)?.toInt() ?? 0,
      proteinGrams: (json['proteinGrams'] as num?)?.toDouble() ?? 0,
      proteinTarget: (json['proteinTarget'] as num?)?.toDouble() ?? 0,
      carbsGrams: (json['carbsGrams'] as num?)?.toDouble() ?? 0,
      carbsTarget: (json['carbsTarget'] as num?)?.toDouble() ?? 0,
      fatGrams: (json['fatGrams'] as num?)?.toDouble() ?? 0,
      fatTarget: (json['fatTarget'] as num?)?.toDouble() ?? 0,
      meals: rawMeals is List
          ? rawMeals
              .whereType<Map>()
              .map((item) => Meal.fromJson(Map<String, dynamic>.from(item)))
              .toList(growable: false)
          : const [],
    );
  }
}

class Meal {
  final int? id;
  final String name;
  final int calories;
  final String time;
  final String imageUrl;

  const Meal({
    this.id,
    required this.name,
    required this.calories,
    required this.time,
    required this.imageUrl,
  });

  factory Meal.fromJson(Map<String, dynamic> json) {
    return Meal(
      id: (json['id'] as num?)?.toInt(),
      name: json['name'] as String? ?? '',
      calories: (json['calories'] as num?)?.toInt() ?? 0,
      time: json['time'] as String? ?? '',
      imageUrl: json['imageUrl'] as String? ?? '',
    );
  }
}
