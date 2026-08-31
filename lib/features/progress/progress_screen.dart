import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:brawlerz_box/shared/models/user_metrics.dart';
import 'package:brawlerz_box/shared/repositories/user_metrics_repository.dart';
import 'package:brawlerz_box/shared/widgets/async_content.dart';
import 'package:brawlerz_box/shared/widgets/brawlerz_card.dart';

class ProgressScreen extends ConsumerWidget {
  const ProgressScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final metrics = ref.watch(userMetricsProvider);
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'YOUR PROGRESS',
          style: GoogleFonts.oswald(fontWeight: FontWeight.bold),
        ),
      ),
      body: metrics.when(
        loading: () => const AsyncLoadingView(),
        error: (error, _) => AsyncErrorView(
          error: error,
          onRetry: () => ref.invalidate(userMetricsProvider),
        ),
        data: (data) => RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(userMetricsProvider);
            await ref.read(userMetricsProvider.future);
          },
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildWeeklySummary(data),
                const SizedBox(height: 24),
                Text(
                  'STRENGTH GAINS',
                  style: GoogleFonts.oswald(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),
                _buildChartCard(
                  'Max Bench Press (kg)',
                  data.strengthHistory,
                  Colors.blue,
                ),
                const SizedBox(height: 24),
                Text(
                  'BODY COMPOSITION',
                  style: GoogleFonts.oswald(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),
                _buildChartCard(
                  'Body Weight (kg)',
                  data.weightHistory,
                  const Color(0xFFFF4500),
                ),
                const SizedBox(height: 40),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildWeeklySummary(UserMetrics metrics) {
    return BrawlerzCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'CURRENT SUMMARY',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _summaryItem(
                'READINESS',
                '${metrics.readinessScore}',
                Icons.speed,
              ),
              _summaryItem('HRV', '${metrics.hrv}', Icons.favorite),
              _summaryItem(
                'RECOVERY',
                '${metrics.recoveryPercentage}%',
                Icons.battery_charging_full,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _summaryItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, size: 20, color: const Color(0xFFFF4500)),
        const SizedBox(height: 8),
        Text(
          value,
          style: GoogleFonts.oswald(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(label, style: const TextStyle(fontSize: 10, color: Colors.grey)),
      ],
    );
  }

  Widget _buildChartCard(
    String title,
    List<ProgressDataPoint> data,
    Color color,
  ) {
    return BrawlerzCard(
      height: 250,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 20),
          Expanded(
            child: data.isEmpty
                ? const Center(child: Text('No data recorded.'))
                : LineChart(
                    LineChartData(
                      gridData: FlGridData(
                        show: true,
                        drawVerticalLine: false,
                        getDrawingHorizontalLine: (value) => FlLine(
                          color: Colors.grey[800],
                          strokeWidth: 1,
                        ),
                      ),
                      titlesData: FlTitlesData(show: false),
                      borderData: FlBorderData(show: false),
                      lineBarsData: [
                        LineChartBarData(
                          spots: data.map((p) => FlSpot(p.x, p.y)).toList(),
                          isCurved: true,
                          color: color,
                          barWidth: 3,
                          isStrokeCapRound: true,
                          dotData: FlDotData(show: true),
                          belowBarData: BarAreaData(
                            show: true,
                            color: color.withOpacity(0.1),
                          ),
                        ),
                      ],
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}
