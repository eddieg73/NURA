import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:brawlerz_box/core/api/api_client.dart';
import 'package:brawlerz_box/shared/models/nutrition_data.dart';

abstract class INutritionRepository {
  Future<NutritionData> getNutritionData();
  Future<NutritionData> updateNutrition(Map<String, dynamic> changes);
  Future<Meal> addMeal(Meal meal);
  Future<void> deleteMeal(int mealId);
}

class NutritionRepository implements INutritionRepository {
  final ApiClient _api;

  NutritionRepository(this._api);

  @override
  Future<NutritionData> getNutritionData() async {
    final payload = await _api.request('GET', '/api/v1/nutrition')
        as Map<String, dynamic>;
    return NutritionData.fromJson(payload);
  }

  @override
  Future<NutritionData> updateNutrition(Map<String, dynamic> changes) async {
    final payload = await _api.request(
      'PUT',
      '/api/v1/nutrition',
      body: changes,
    ) as Map<String, dynamic>;
    return NutritionData.fromJson(payload);
  }

  @override
  Future<Meal> addMeal(Meal meal) async {
    final payload = await _api.request(
      'POST',
      '/api/v1/nutrition/meals',
      body: {
        'name': meal.name,
        'calories': meal.calories,
        'time': meal.time,
        'imageUrl': meal.imageUrl,
      },
    ) as Map<String, dynamic>;
    return Meal.fromJson(payload);
  }

  @override
  Future<void> deleteMeal(int mealId) async {
    await _api.request('DELETE', '/api/v1/nutrition/meals/$mealId');
  }
}

final nutritionRepositoryProvider = Provider<INutritionRepository>((ref) {
  return NutritionRepository(ref.watch(apiClientProvider));
});

final nutritionDataProvider = FutureProvider<NutritionData>((ref) {
  return ref.watch(nutritionRepositoryProvider).getNutritionData();
});
