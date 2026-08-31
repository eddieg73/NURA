import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:brawlerz_box/shared/repositories/admin_repository.dart';
import 'package:brawlerz_box/shared/widgets/async_content.dart';
import 'package:brawlerz_box/shared/widgets/brawlerz_card.dart';

class AdminDashboardScreen extends ConsumerWidget {
  const AdminDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final summary = ref.watch(adminSummaryProvider);
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'BUSINESS DASHBOARD',
          style: GoogleFonts.oswald(fontWeight: FontWeight.bold),
        ),
      ),
      body: summary.when(
        loading: () => const AsyncLoadingView(),
        error: (error, _) => AsyncErrorView(
          error: error,
          onRetry: () => ref.invalidate(adminSummaryProvider),
        ),
        data: (data) => RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(adminSummaryProvider);
            await ref.read(adminSummaryProvider.future);
          },
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildStatGrid(data),
                const SizedBox(height: 24),
                Text(
                  'TOP CLASSES',
                  style: GoogleFonts.oswald(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),
                _buildTopClasses(data['topClasses']),
                const SizedBox(height: 24),
                const BrawlerzCard(
                  color: Color(0x1AFFB000),
                  child: Text(
                    'Revenue reflects backend orders only. Payment capture, refunds, taxes and subscription billing require a payment processor integration before production use.',
                    style: TextStyle(fontSize: 12),
                  ),
                ),
                const SizedBox(height: 40),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatGrid(Map<String, dynamic> data) {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      childAspectRatio: 1.5,
      children: [
        _statCard(
          'TOTAL MEMBERS',
          '${data['totalMembers'] ?? 0}',
          Icons.people,
          Colors.blue,
        ),
        _statCard(
          'CHECK-INS TODAY',
          '${data['checkInsToday'] ?? 0}',
          Icons.qr_code_scanner,
          Colors.green,
        ),
        _statCard(
          'ORDER REVENUE',
          '\$${((data['revenue'] as num?)?.toDouble() ?? 0).toStringAsFixed(2)}',
          Icons.attach_money,
          const Color(0xFFFF4500),
        ),
        _statCard(
          'SERVICE STATUS',
          'ONLINE',
          Icons.cloud_done,
          Colors.purple,
        ),
      ],
    );
  }

  Widget _statCard(String label, String value, IconData icon, Color color) {
    return BrawlerzCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 20, color: color),
          const SizedBox(height: 8),
          Text(
            value,
            style: GoogleFonts.oswald(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            label,
            style: const TextStyle(
              fontSize: 10,
              color: Colors.grey,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTopClasses(dynamic raw) {
    final classes = raw is List ? raw.whereType<Map>().toList() : const <Map>[];
    return BrawlerzCard(
      child: Column(
        children: classes.isEmpty
            ? const [Text('No class data available.')]
            : classes.map((item) {
                final time = item['time'] is String
                    ? DateTime.tryParse(item['time'] as String)
                    : null;
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              item['name']?.toString() ?? 'Class',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 14,
                              ),
                            ),
                            if (time != null)
                              Text(
                                DateFormat('MMM d • h:mm a').format(time.toLocal()),
                                style: TextStyle(
                                  color: Colors.grey[500],
                                  fontSize: 12,
                                ),
                              ),
                          ],
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.grey[800],
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          '${item['attendance'] ?? 0}/${item['capacity'] ?? 0}',
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
      ),
    );
  }
}
