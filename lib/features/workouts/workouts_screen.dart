import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:brawlerz_box/shared/repositories/workout_repository.dart';
import 'package:brawlerz_box/shared/widgets/async_content.dart';
import 'package:brawlerz_box/shared/widgets/brawlerz_card.dart';

class WorkoutsScreen extends ConsumerWidget {
  const WorkoutsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final workouts = ref.watch(workoutPlansProvider);
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'WORKOUT PLANS',
          style: GoogleFonts.oswald(fontWeight: FontWeight.bold),
        ),
      ),
      body: workouts.when(
        loading: () => const AsyncLoadingView(),
        error: (error, _) => AsyncErrorView(
          error: error,
          onRetry: () => ref.invalidate(workoutPlansProvider),
        ),
        data: (plans) => RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(workoutPlansProvider);
            await ref.read(workoutPlansProvider.future);
          },
          child: ListView.builder(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(20),
            itemCount: plans.length,
            itemBuilder: (context, index) {
              final workout = plans[index];
              return Padding(
                padding: const EdgeInsets.only(bottom: 20),
                child: BrawlerzCard(
                  padding: EdgeInsets.zero,
                  onTap: () {},
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (workout.imageUrl.isNotEmpty)
                        Stack(
                          children: [
                            ClipRRect(
                              borderRadius: const BorderRadius.vertical(
                                top: Radius.circular(12),
                              ),
                              child: Image.network(
                                workout.imageUrl,
                                height: 180,
                                width: double.infinity,
                                fit: BoxFit.cover,
                                errorBuilder: (_, __, ___) => const SizedBox(
                                  height: 180,
                                  child: Center(
                                    child: Icon(Icons.fitness_center, size: 48),
                                  ),
                                ),
                              ),
                            ),
                            Positioned(
                              top: 12,
                              right: 12,
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 10,
                                  vertical: 4,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.black.withOpacity(0.7),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  workout.category.toUpperCase(),
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              workout.title.toUpperCase(),
                              style: GoogleFonts.oswald(
                                fontSize: 22,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              workout.description,
                              style: TextStyle(
                                color: Colors.grey[400],
                                fontSize: 14,
                              ),
                            ),
                            const SizedBox(height: 16),
                            Row(
                              children: [
                                const Icon(
                                  Icons.timer_outlined,
                                  size: 16,
                                  color: Color(0xFFFF4500),
                                ),
                                const SizedBox(width: 4),
                                Text(
                                  workout.duration,
                                  style: const TextStyle(fontSize: 12),
                                ),
                                const SizedBox(width: 16),
                                const Icon(
                                  Icons.bolt,
                                  size: 16,
                                  color: Color(0xFFFF4500),
                                ),
                                const SizedBox(width: 4),
                                Text(
                                  workout.level,
                                  style: const TextStyle(fontSize: 12),
                                ),
                                const Spacer(),
                                const Text(
                                  'VIEW PLAN',
                                  style: TextStyle(
                                    color: Color(0xFFFF4500),
                                    fontWeight: FontWeight.bold,
                                    fontSize: 12,
                                    letterSpacing: 1.1,
                                  ),
                                ),
                                const Icon(
                                  Icons.chevron_right,
                                  size: 16,
                                  color: Color(0xFFFF4500),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}
