import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:brawlerz_box/shared/models/user_metrics.dart';
import 'package:brawlerz_box/shared/models/workout_plan.dart';
import 'package:brawlerz_box/shared/repositories/user_metrics_repository.dart';
import 'package:brawlerz_box/shared/repositories/workout_repository.dart';
import 'package:brawlerz_box/shared/widgets/async_content.dart';
import 'package:brawlerz_box/shared/widgets/brawlerz_card.dart';
import 'package:brawlerz_box/shared/widgets/metric_tile.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final metrics = ref.watch(userMetricsProvider);
    final workouts = ref.watch(workoutPlansProvider);

    return metrics.when(
      loading: () => const Scaffold(body: AsyncLoadingView()),
      error: (error, _) => Scaffold(
        body: AsyncErrorView(
          error: error,
          onRetry: () {
            ref.invalidate(userMetricsProvider);
            ref.invalidate(workoutPlansProvider);
          },
        ),
      ),
      data: (metricData) => workouts.when(
        loading: () => const Scaffold(body: AsyncLoadingView()),
        error: (error, _) => Scaffold(
          body: AsyncErrorView(
            error: error,
            onRetry: () => ref.invalidate(workoutPlansProvider),
          ),
        ),
        data: (plans) => _DashboardContent(
          metrics: metricData,
          todayWorkout: plans.isEmpty ? null : plans.first,
          onRefresh: () async {
            ref.invalidate(userMetricsProvider);
            ref.invalidate(workoutPlansProvider);
            await ref.read(userMetricsProvider.future);
            await ref.read(workoutPlansProvider.future);
          },
        ),
      ),
    );
  }
}

class _DashboardContent extends StatelessWidget {
  final UserMetrics metrics;
  final WorkoutPlan? todayWorkout;
  final Future<void> Function() onRefresh;

  const _DashboardContent({
    required this.metrics,
    required this.todayWorkout,
    required this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: RefreshIndicator(
        onRefresh: onRefresh,
        child: CustomScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          slivers: [
            SliverAppBar(
              expandedHeight: 120,
              pinned: true,
              backgroundColor: const Color(0xFF121212),
              flexibleSpace: FlexibleSpaceBar(
                titlePadding: const EdgeInsets.symmetric(
                  horizontal: 20,
                  vertical: 16,
                ),
                title: Text(
                  'MEMBER DASHBOARD',
                  style: GoogleFonts.oswald(
                    fontWeight: FontWeight.bold,
                    fontSize: 20,
                    color: Colors.white,
                  ),
                ),
                centerTitle: false,
              ),
            ),
            SliverPadding(
              padding: const EdgeInsets.all(20),
              sliver: SliverList(
                delegate: SliverChildListDelegate([
                  _buildReadinessCard(context, metrics.readinessScore),
                  const SizedBox(height: 24),
                  Row(
                    children: [
                      Expanded(
                        child: BrawlerzCard(
                          child: MetricTile(
                            label: 'HRV',
                            value: '${metrics.hrv}',
                            unit: 'ms',
                            icon: Icons.favorite,
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: BrawlerzCard(
                          child: MetricTile(
                            label: 'Sleep',
                            value: '${metrics.sleepScore}',
                            unit: '/100',
                            icon: Icons.nightlight_round,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  Text(
                    'TODAY\'S SESSION',
                    style: GoogleFonts.oswald(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.2,
                    ),
                  ),
                  const SizedBox(height: 16),
                  if (todayWorkout == null)
                    const BrawlerzCard(child: Text('No active workout plan.'))
                  else
                    _buildWorkoutCard(context, todayWorkout!),
                  const SizedBox(height: 24),
                  Text(
                    'QUICK ACTIONS',
                    style: GoogleFonts.oswald(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.2,
                    ),
                  ),
                  const SizedBox(height: 16),
                  _buildQuickActions(context),
                  const SizedBox(height: 40),
                ]),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildReadinessCard(BuildContext context, int score) {
    return BrawlerzCard(
      padding: const EdgeInsets.all(20),
      color: const Color(0xFF1E1E1E),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'READINESS SCORE',
                  style: TextStyle(
                    color: Colors.grey[400],
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                    letterSpacing: 1.1,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  score >= 75 ? 'Ready to push' : 'Recovery focus',
                  style: GoogleFonts.oswald(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Synced from your backend profile.',
                  style: TextStyle(color: Colors.grey[500], fontSize: 14),
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 70,
                height: 70,
                child: CircularProgressIndicator(
                  value: score.clamp(0, 100) / 100,
                  strokeWidth: 8,
                  backgroundColor: Colors.grey[800],
                  color: const Color(0xFFFF4500),
                ),
              ),
              Text(
                '$score',
                style: GoogleFonts.oswald(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildWorkoutCard(BuildContext context, WorkoutPlan workout) {
    return BrawlerzCard(
      padding: EdgeInsets.zero,
      onTap: () => context.go('/workouts'),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (workout.imageUrl.isNotEmpty)
            ClipRRect(
              borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
              child: Image.network(
                workout.imageUrl,
                height: 160,
                width: double.infinity,
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => const SizedBox(
                  height: 160,
                  child: Center(child: Icon(Icons.fitness_center, size: 48)),
                ),
              ),
            ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        workout.title.toUpperCase(),
                        style: GoogleFonts.oswald(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${workout.duration} • ${workout.level}',
                        style: TextStyle(color: Colors.grey[400], fontSize: 14),
                      ),
                    ],
                  ),
                ),
                ElevatedButton(
                  onPressed: () {},
                  child: const Text('START'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions(BuildContext context) {
    final actions = <({IconData icon, String label, String path})>[
      (icon: Icons.restaurant, label: 'Nutrition', path: '/nutrition'),
      (icon: Icons.shopping_bag, label: 'Shop', path: '/supplements'),
      (icon: Icons.calendar_month, label: 'Classes', path: '/classes'),
      (icon: Icons.videocam, label: 'AI Coach', path: '/ai-coach'),
    ];

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        childAspectRatio: 2.5,
      ),
      itemCount: actions.length,
      itemBuilder: (context, index) {
        final action = actions[index];
        return BrawlerzCard(
          onTap: () => context.push(action.path),
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              Icon(action.icon, color: const Color(0xFFFF4500)),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  action.label,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
