import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:brawlerz_box/shared/widgets/brawlerz_card.dart';

class AdminDashboardScreen extends StatelessWidget {
  const AdminDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'BUSINESS DASHBOARD',
          style: GoogleFonts.oswald(fontWeight: FontWeight.bold),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildStatGrid(),
            const SizedBox(height: 24),
            Text(
              'REVENUE GROWTH',
              style: GoogleFonts.oswald(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildRevenueChart(),
            const SizedBox(height: 24),
            Text(
              'ACTIVE MEMBERSHIPS',
              style: GoogleFonts.oswald(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildMembershipChart(),
            const SizedBox(height: 24),
            Text(
              'TOP CLASSES TODAY',
              style: GoogleFonts.oswald(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildTopClassesList(),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildStatGrid() {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      childAspectRatio: 1.5,
      children: [
        _statCard('TOTAL MEMBERS', '1,284', Icons.people, Colors.blue),
        _statCard('CHECK-INS TODAY', '142', Icons.qr_code_scanner, Colors.green),
        _statCard('MONTHLY REVENUE', '\$42.5k', Icons.attach_money, const Color(0xFFFF4500)),
        _statCard('ACTIVE SUBS', '94%', Icons.check_circle, Colors.purple),
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
            style: GoogleFonts.oswald(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          Text(
            label,
            style: const TextStyle(fontSize: 10, color: Colors.grey, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Widget _buildRevenueChart() {
    return BrawlerzCard(
      height: 200,
      child: LineChart(
        LineChartData(
          gridData: FlGridData(show: false),
          titlesData: FlTitlesData(show: false),
          borderData: FlBorderData(show: false),
          lineBarsData: [
            LineChartBarData(
              spots: const [
                FlSpot(0, 30),
                FlSpot(1, 35),
                FlSpot(2, 32),
                FlSpot(3, 40),
                FlSpot(4, 38),
                FlSpot(5, 42.5),
              ],
              isCurved: true,
              color: const Color(0xFFFF4500),
              barWidth: 4,
              dotData: FlDotData(show: false),
              belowBarData: BarAreaData(
                show: true,
                color: const Color(0xFFFF4500).withOpacity(0.1),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMembershipChart() {
    return BrawlerzCard(
      height: 150,
      child: BarChart(
        BarChartData(
          gridData: FlGridData(show: false),
          titlesData: FlTitlesData(show: false),
          borderData: FlBorderData(show: false),
          barGroups: [
            BarChartGroupData(x: 0, barRods: [BarChartRodData(toY: 8, color: Colors.blue)]),
            BarChartGroupData(x: 1, barRods: [BarChartRodData(toY: 10, color: Colors.blue)]),
            BarChartGroupData(x: 2, barRods: [BarChartRodData(toY: 14, color: Colors.blue)]),
            BarChartGroupData(x: 3, barRods: [BarChartRodData(toY: 15, color: Colors.blue)]),
            BarChartGroupData(x: 4, barRods: [BarChartRodData(toY: 13, color: Colors.blue)]),
            BarChartGroupData(x: 5, barRods: [BarChartRodData(toY: 18, color: Colors.blue)]),
          ],
        ),
      ),
    );
  }

  Widget _buildTopClassesList() {
    final classes = [
      {'name': 'Boxing Fundamentals', 'attendance': '24/25', 'time': '6:00 PM'},
      {'name': 'HIIT Training', 'attendance': '18/20', 'time': '9:00 AM'},
      {'name': 'MMA Conditioning', 'attendance': '15/15', 'time': '5:30 PM'},
    ];

    return BrawlerzCard(
      child: Column(
        children: classes.map((c) => Padding(
          padding: const EdgeInsets.symmetric(vertical: 8.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(c['name']!, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                  Text(c['time']!, style: TextStyle(color: Colors.grey[500], fontSize: 12)),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.grey[800],
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  c['attendance']!,
                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
        )).toList(),
      ),
    );
  }
}
