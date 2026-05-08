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

  NutritionData({
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
}

class Meal {
  final String name;
  final int calories;
  final String time;
  final String imageUrl;

  Meal({
    required this.name,
    required this.calories,
    required this.time,
    required this.imageUrl,
  });
}
