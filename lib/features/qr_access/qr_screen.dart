import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:brawlerz_box/shared/widgets/brawlerz_card.dart';

class QrScreen extends StatelessWidget {
  const QrScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'GYM ACCESS',
          style: GoogleFonts.oswald(fontWeight: FontWeight.bold),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            const SizedBox(height: 20),
            Text(
              'BRAWLERZ BOX',
              style: GoogleFonts.oswald(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                letterSpacing: 2,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Scan to enter the facility',
              style: TextStyle(color: Colors.grey[400]),
            ),
            const SizedBox(height: 40),
            BrawlerzCard(
              padding: const EdgeInsets.all(32),
              color: Colors.white,
              child: QrImageView(
                data: 'MEMBER_ID_12345_BRAWLERZ',
                version: QrVersions.auto,
                size: 200.0,
                foregroundColor: Colors.black,
              ),
            ),
            const SizedBox(height: 40),
            _buildStatusCard(),
            const SizedBox(height: 24),
            _buildHistoryCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusCard() {
    return BrawlerzCard(
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.green.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.check_circle, color: Colors.green),
          ),
          const SizedBox(width: 16),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'ACTIVE MEMBERSHIP',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              Text(
                '24/7 Access Enabled',
                style: TextStyle(color: Colors.grey[400], fontSize: 12),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryCard() {
    return BrawlerzCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'RECENT CHECK-INS',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, letterSpacing: 1.1),
          ),
          const SizedBox(height: 16),
          _historyItem('Yesterday', '6:30 PM'),
          const Divider(height: 24, color: Colors.grey),
          _historyItem('Oct 24, 2023', '7:15 AM'),
          const Divider(height: 24, color: Colors.grey),
          _historyItem('Oct 22, 2023', '6:00 PM'),
        ],
      ),
    );
  }

  Widget _historyItem(String date, String time) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(date, style: const TextStyle(color: Colors.white)),
        Text(time, style: TextStyle(color: Colors.grey[400])),
      ],
    );
  }
}
