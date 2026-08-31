import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:brawlerz_box/core/api/api_client.dart';
import 'package:brawlerz_box/shared/models/workout_plan.dart';

abstract class IWorkoutRepository {
  Future<List<WorkoutPlan>> getWorkoutPlans();
}

class WorkoutRepository implements IWorkoutRepository {
  final ApiClient _api;

  WorkoutRepository(this._api);

  @override
  Future<List<WorkoutPlan>> getWorkoutPlans() async {
    final payload = await _api.request('GET', '/api/v1/workouts') as List;
    return payload
        .whereType<Map>()
        .map((item) => WorkoutPlan.fromJson(
              Map<String, dynamic>.from(item),
            ))
        .toList(growable: false);
  }
}

final workoutRepositoryProvider = Provider<IWorkoutRepository>((ref) {
  return WorkoutRepository(ref.watch(apiClientProvider));
});

final workoutPlansProvider = FutureProvider<List<WorkoutPlan>>((ref) {
  return ref.watch(workoutRepositoryProvider).getWorkoutPlans();
});
