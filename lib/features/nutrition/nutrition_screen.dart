import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:brawlerz_box/shared/widgets/brawlerz_card.dart';
import 'package:brawlerz_box/shared/repositories/nutrition_repository.dart';

class NutritionScreen extends ConsumerWidget {
  const NutritionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(nutritionRepositoryProvider).getNutritionData();

    return Scaffold(
      appBar: AppBar(
        title: Text(
          'NUTRITION',
          style: GoogleFonts.oswald(fontWeight: FontWeight.bold),
        ),
      ),
      body: ListView(
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
          ...data.meals.map((meal) => _buildMealCard(meal)).toList(),
          const SizedBox(height: 24),
          BrawlerzCard(
            color: const Color(0xFF1E1E1E),
            onTap: () {},
            child: Row(
              children: [
                const Icon(Icons.shopping_cart, color: Color(0xFFFF4500)),
                const SizedBox(width: 16),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'GROCERY INTEGRATION',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                      ),
                      Text(
                        'Order ingredients via Instacart or Amazon',
                        style: TextStyle(color: Colors.grey, fontSize: 12),
                      ),
                    ],
                  ),
                ),
                const Icon(Icons.chevron_right, color: Colors.grey),
              ],
            ),
          ),
          const SizedBox(height: 40),
        ],
      ),
    );
  }

  Widget _buildDailySummary(dynamic data) {
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
                    style: TextStyle(color: Colors.grey, fontSize: 10, fontWeight: FontWeight.bold),
                  ),
                  Text(
                    '${data.targetCalories - data.dailyCalories}',
                    style: GoogleFonts.oswald(fontSize: 32, fontWeight: FontWeight.bold),
                  ),
                  const Text('kcal', style: TextStyle(color: Colors.grey, fontSize: 12)),
                ],
              ),
              SizedBox(
                width: 80,
                height: 80,
                child: CircularProgressIndicator(
                  value: data.dailyCalories / data.targetCalories,
                  strokeWidth: 10,
                  backgroundColor: Colors.grey[800],
                  color: const Color(0xFFFF4500),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          _buildMacroRow('PROTEIN', data.proteinGrams, data.proteinTarget, Colors.blue),
          const SizedBox(height: 12),
          _buildMacroRow('CARBS', data.carbsGrams, data.carbsTarget, Colors.green),
          const SizedBox(height: 12),
          _buildMacroRow('FAT', data.fatGrams, data.fatTarget, Colors.orange),
        ],
      ),
    );
  }

  Widget _buildMacroRow(String label, double current, double target, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
            Text('${current.toInt()}g / ${target.toInt()}g', style: const TextStyle(fontSize: 10)),
          ],
        ),
        const SizedBox(height: 4),
        LinearProgressIndicator(
          value: current / target,
          backgroundColor: Colors.grey[800],
          color: color,
          minHeight: 6,
          borderRadius: BorderRadius.circular(3),
        ),
      ],
    );
  }

  Widget _buildMealCard(dynamic meal) {
    return Padding(
      padding: const EdgeInsets.bottom(16.0),
      child: BrawlerzCard(
        padding: EdgeInsets.zero,
        child: Row(
          children: [
            ClipRRect(
              borderRadius: const BorderRadius.horizontal(left: Radius.circular(12)),
              child: Image.network(
                meal.imageUrl,
                width: 80,
                height: 80,
                fit: BoxFit.cover,
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
              padding: const EdgeInsets.only(right: 16.0),
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
