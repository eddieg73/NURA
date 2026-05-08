import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:brawlerz_box/shared/models/workout_plan.dart';

abstract class IWorkoutRepository {
  List<WorkoutPlan> getWorkoutPlans();
}

class WorkoutRepository implements IWorkoutRepository {
  @override
  List<WorkoutPlan> getWorkoutPlans() {
    // TODO: Implement actual API call for workouts
    return [
      WorkoutPlan(
        id: '1',
        title: 'Boxing Fundamentals',
        description: 'Master the basics of boxing footwork and punches.',
        level: 'Beginner',
        duration: '45 min',
        imageUrl: 'https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=500',
        category: 'Boxing',
      ),
      WorkoutPlan(
        id: '2',
        title: 'Heavy Bag Power',
        description: 'High intensity drills to build explosive power.',
        level: 'Intermediate',
        duration: '30 min',
        imageUrl: 'https://images.unsplash.com/photo-1517438322351-db62136e01a0?w=500',
        category: 'Boxing',
      ),
      WorkoutPlan(
        id: '3',
        title: 'Full Body Strength',
        description: 'Compound lifts and functional movements.',
        level: 'Beginner',
        duration: '60 min',
        imageUrl: 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=500',
        category: 'Strength',
      ),
      WorkoutPlan(
        id: '4',
        title: 'HIIT Conditioning',
        description: 'Fast-paced circuits to burn fat and increase stamina.',
        level: 'Advanced',
        duration: '25 min',
        imageUrl: 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500',
        category: 'HIIT',
      ),
    ];
  }
}

final workoutRepositoryProvider = Provider<IWorkoutRepository>((ref) => WorkoutRepository());
