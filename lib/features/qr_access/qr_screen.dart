import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:brawlerz_box/shared/repositories/qr_repository.dart';
import 'package:brawlerz_box/shared/widgets/async_content.dart';
import 'package:brawlerz_box/shared/widgets/brawlerz_card.dart';

class QrScreen extends ConsumerWidget {
  const QrScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pass = ref.watch(qrPassProvider);
    final history = ref.watch(qrHistoryProvider);
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'GYM ACCESS',
          style: GoogleFonts.oswald(fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            tooltip: 'Generate new pass',
            onPressed: () => ref.invalidate(qrPassProvider),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: pass.when(
        loading: () => const AsyncLoadingView(),
        error: (error, _) => AsyncErrorView(
          error: error,
          onRetry: () => ref.invalidate(qrPassProvider),
        ),
        data: (qrPass) => SingleChildScrollView(
          padding: const EdgeInsets.all(24),
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
                'One-time pass • expires ${DateFormat('h:mm a').format(qrPass.expiresAt.toLocal())}',
                style: TextStyle(color: Colors.grey[400]),
              ),
              const SizedBox(height: 40),
              BrawlerzCard(
                padding: const EdgeInsets.all(32),
                color: Colors.white,
                child: QrImageView(
                  data: qrPass.token,
                  version: QrVersions.auto,
                  size: 220,
                  foregroundColor: Colors.black,
                ),
              ),
              const SizedBox(height: 40),
              const BrawlerzCard(
                child: Row(
                  children: [
                    Icon(Icons.security, color: Colors.green),
                    SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'SERVER-ISSUED ACCESS PASS',
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                          SizedBox(height: 4),
                          Text(
                            'The pass expires and is revoked after successful validation.',
                            style: TextStyle(color: Colors.grey, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              history.when(
                loading: () => const BrawlerzCard(
                  child: Center(child: CircularProgressIndicator()),
                ),
                error: (error, _) => BrawlerzCard(
                  child: Text('Unable to load check-ins: $error'),
                ),
                data: _buildHistory,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHistory(List<DateTime> checkIns) {
    return BrawlerzCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'RECENT CHECK-INS',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 12,
              letterSpacing: 1.1,
            ),
          ),
          const SizedBox(height: 16),
          if (checkIns.isEmpty)
            const Text(
              'No check-ins recorded yet.',
              style: TextStyle(color: Colors.grey),
            )
          else
            ...checkIns.map(
              (value) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(DateFormat('MMM d, yyyy').format(value.toLocal())),
                    Text(
                      DateFormat('h:mm a').format(value.toLocal()),
                      style: TextStyle(color: Colors.grey[400]),
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
