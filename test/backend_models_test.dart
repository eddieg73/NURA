import 'package:flutter_test/flutter_test.dart';
import 'package:brawlerz_box/shared/models/class_session.dart';
import 'package:brawlerz_box/shared/models/nutrition_data.dart';
import 'package:brawlerz_box/shared/models/supplement.dart';
import 'package:brawlerz_box/shared/models/user_metrics.dart';
import 'package:brawlerz_box/shared/models/workout_plan.dart';

void main() {
  test('backend JSON contracts deserialize into Flutter models', () {
    final session = ClassSession.fromJson({
      'id': 'c1',
      'name': 'Boxing',
      'startTime': '2026-08-31T12:00:00Z',
      'trainer': 'Coach',
      'durationMinutes': 60,
      'capacity': 25,
      'reservedCount': 4,
      'isReserved': true,
    });
    expect(session.isReserved, isTrue);
    expect(session.capacity, 25);

    final workout = WorkoutPlan.fromJson({
      'id': 'w1',
      'title': 'Strength',
      'description': 'Plan',
      'level': 'Beginner',
      'duration': '30 min',
      'imageUrl': '',
      'category': 'Strength',
    });
    expect(workout.title, 'Strength');

    final supplement = Supplement.fromJson({
      'id': 's1',
      'name': 'Protein',
      'description': 'Nutrition',
      'price': 39.99,
      'imageUrl': '',
      'tags': ['Tested'],
      'inventory': 10,
      'inStock': true,
    });
    expect(supplement.tags, ['Tested']);

    final nutrition = NutritionData.fromJson({
      'dailyCalories': 1000,
      'targetCalories': 2000,
      'proteinGrams': 80,
      'proteinTarget': 160,
      'carbsGrams': 100,
      'carbsTarget': 200,
      'fatGrams': 40,
      'fatTarget': 80,
      'meals': [
        {
          'id': 1,
          'name': 'Breakfast',
          'calories': 500,
          'time': '8:00 AM',
          'imageUrl': '',
        },
      ],
    });
    expect(nutrition.meals.single.name, 'Breakfast');

    final metrics = UserMetrics.fromJson({
      'readinessScore': 88,
      'hrv': 65,
      'sleepScore': 82,
      'recoveryPercentage': 75,
      'strengthHistory': [
        {'x': 0, 'y': 100},
      ],
      'weightHistory': [
        {'x': 0, 'y': 85},
      ],
    });
    expect(metrics.strengthHistory.single.y, 100);
  });
}
