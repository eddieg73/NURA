import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:brawlerz_box/shared/models/nutrition_data.dart';
import 'package:brawlerz_box/shared/repositories/nutrition_repository.dart';
import 'package:brawlerz_box/shared/widgets/async_content.dart';
import 'package:brawlerz_box/shared/widgets/brawlerz_card.dart';

class NutritionScreen extends ConsumerWidget {
  const NutritionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final nutrition = ref.watch(nutritionDataProvider);
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'NUTRITION',
          style: GoogleFonts.oswald(fontWeight: FontWeight.bold),
        ),
      ),
      body: nutrition.when(
        loading: () => const AsyncLoadingView(),
        error: (error, _) => AsyncErrorView(
          error: error,
          onRetry: () => ref.invalidate(nutritionDataProvider),
        ),
        data: (data) => RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(nutritionDataProvider);
            await ref.read(nutritionDataProvider.future);
          },
          child: ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(20),
            children: [
              _buildDailySummary(data),
              const SizedBox(height: 24),
              Text(
                'TODAY\'S MEALS',
                style: GoogleFonts.oswald(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 16),
              ...data.meals.map(_buildMealCard),
              const SizedBox(height: 24),
              const BrawlerzCard(
                color: Color(0xFF1E1E1E),
                child: Row(
                  children: [
                    Icon(Icons.cloud_done, color: Color(0xFFFF4500)),
                    SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'BACKEND SYNC ENABLED',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                            ),
                          ),
                          Text(
                            'Meals and macro targets are stored per account.',
                            style: TextStyle(color: Colors.grey, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDailySummary(NutritionData data) {
    final calorieProgress = data.targetCalories <= 0
        ? 0.0
        : (data.dailyCalories / data.targetCalories).clamp(0.0, 1.0);
    return BrawlerzCard(
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'REMAINING',
                    style: TextStyle(
                      color: Colors.grey,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    '${data.targetCalories - data.dailyCalories}',
                    style: GoogleFonts.oswald(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const Text(
                    'kcal',
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ],
              ),
              SizedBox(
                width: 80,
                height: 80,
                child: CircularProgressIndicator(
                  value: calorieProgress,
                  strokeWidth: 10,
                  backgroundColor: Colors.grey[800],
                  color: const Color(0xFFFF4500),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          _buildMacroRow(
            'PROTEIN',
            data.proteinGrams,
            data.proteinTarget,
            Colors.blue,
          ),
          const SizedBox(height: 12),
          _buildMacroRow(
            'CARBS',
            data.carbsGrams,
            data.carbsTarget,
            Colors.green,
          ),
          const SizedBox(height: 12),
          _buildMacroRow(
            'FAT',
            data.fatGrams,
            data.fatTarget,
            Colors.orange,
          ),
        ],
      ),
    );
  }

  Widget _buildMacroRow(
    String label,
    double current,
    double target,
    Color color,
  ) {
    final value = target <= 0 ? 0.0 : (current / target).clamp(0.0, 1.0);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: const TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              '${current.toInt()}g / ${target.toInt()}g',
              style: const TextStyle(fontSize: 10),
            ),
          ],
        ),
        const SizedBox(height: 4),
        LinearProgressIndicator(
          value: value,
          backgroundColor: Colors.grey[800],
          color: color,
          minHeight: 6,
          borderRadius: BorderRadius.circular(3),
        ),
      ],
    );
  }

  Widget _buildMealCard(Meal meal) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: BrawlerzCard(
        padding: EdgeInsets.zero,
        child: Row(
          children: [
            SizedBox(
              width: 80,
              height: 80,
              child: meal.imageUrl.isEmpty
                  ? const Icon(Icons.restaurant, size: 36)
                  : ClipRRect(
                      borderRadius: const BorderRadius.horizontal(
                        left: Radius.circular(12),
                      ),
                      child: Image.network(
                        meal.imageUrl,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) =>
                            const Icon(Icons.restaurant, size: 36),
                      ),
                    ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    meal.name,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    meal.time,
                    style: TextStyle(color: Colors.grey[500], fontSize: 12),
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(right: 16),
              child: Text(
                '${meal.calories} kcal',
                style: GoogleFonts.oswald(fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
