import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:brawlerz_box/shared/widgets/brawlerz_card.dart';
import 'package:brawlerz_box/shared/widgets/metric_tile.dart';
import 'package:brawlerz_box/shared/repositories/user_metrics_repository.dart';
import 'package:brawlerz_box/shared/repositories/workout_repository.dart';
import 'package:go_router/go_router.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final metrics = ref.watch(userMetricsRepositoryProvider).getUserMetrics();
    final workouts = ref.watch(workoutRepositoryProvider).getWorkoutPlans();
    final todayWorkout = workouts.first;

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 120,
            floating: false,
            pinned: true,
            backgroundColor: const Color(0xFF121212),
            flexibleSpace: FlexibleSpaceBar(
              titlePadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              title: Text(
                'HELLO, JESSICA',
                style: GoogleFonts.oswald(
                  fontWeight: FontWeight.bold,
                  fontSize: 20,
                  color: Colors.white,
                ),
              ),
              centerTitle: false,
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined),
                onPressed: () {},
              ),
              const SizedBox(width: 8),
            ],
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
                _buildWorkoutCard(context, todayWorkout),
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
    );
  }

  Widget _buildReadinessCard(BuildContext context, int score) {
    return BrawlerzCard(
      padding: const EdgeInsets.all(20),
      color: const Color(0xFF1E1E1E),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
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
                'Ready to push',
                style: GoogleFonts.oswald(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Your recovery is optimal today.',
                style: TextStyle(color: Colors.grey[500], fontSize: 14),
              ),
            ],
          ),
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 70,
                height: 70,
                child: CircularProgressIndicator(
                  value: score / 100,
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

  Widget _buildWorkoutCard(BuildContext context, dynamic workout) {
    return BrawlerzCard(
      padding: EdgeInsets.zero,
      onTap: () => context.go('/workouts'),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ClipRRect(
            borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
            child: Image.network(
              workout.imageUrl,
              height: 160,
              width: double.infinity,
              fit: BoxFit.cover,
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
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
    final actions = [
      {'icon': Icons.restaurant, 'label': 'Nutrition', 'path': '/nutrition'},
      {'icon': Icons.shopping_bag, 'label': 'Shop', 'path': '/supplements'},
      {'icon': Icons.calendar_month, 'label': 'Classes', 'path': '/classes'},
      {'icon': Icons.videocam, 'label': 'AI Coach', 'path': '/ai-coach'},
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
        return BrawlerzCard(
          onTap: () => context.push(actions[index]['path'] as String),
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              Icon(actions[index]['icon'] as IconData, color: const Color(0xFFFF4500)),
              const SizedBox(width: 12),
              Text(
                actions[index]['label'] as String,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ],
          ),
        );
      },
    );
  }
}
