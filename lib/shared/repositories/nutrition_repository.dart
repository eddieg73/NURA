import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:brawlerz_box/shared/models/nutrition_data.dart';

abstract class INutritionRepository {
  NutritionData getNutritionData();
}

class NutritionRepository implements INutritionRepository {
  @override
  NutritionData getNutritionData() {
    // TODO: Connect to Nutrition & Macro logging API
    return NutritionData(
      dailyCalories: 1850,
      targetCalories: 2400,
      proteinGrams: 140,
      proteinTarget: 180,
      carbsGrams: 210,
      carbsTarget: 250,
      fatGrams: 55,
      fatTarget: 70,
      meals: [
        Meal(
          name: 'Protein Oatmeal',
          calories: 450,
          time: '08:00 AM',
          imageUrl: 'https://images.unsplash.com/photo-1517673132405-a56a62b18caf?w=500',
        ),
        Meal(
          name: 'Chicken Breast & Quinoa',
          calories: 650,
          time: '01:30 PM',
          imageUrl: 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=500',
        ),
        Meal(
          name: 'Post-Workout Shake',
          calories: 250,
          time: '05:00 PM',
          imageUrl: 'https://images.unsplash.com/photo-1593095948071-474c5cc2989d?w=500',
        ),
      ],
    );
  }
}

final nutritionRepositoryProvider = Provider<INutritionRepository>((ref) => NutritionRepository());
