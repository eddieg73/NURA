import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:brawlerz_box/core/api/api_client.dart';
import 'package:brawlerz_box/shared/models/class_session.dart';
import 'package:brawlerz_box/shared/repositories/class_repository.dart';
import 'package:brawlerz_box/shared/widgets/async_content.dart';
import 'package:brawlerz_box/shared/widgets/brawlerz_card.dart';

class ClassesScreen extends ConsumerStatefulWidget {
  const ClassesScreen({super.key});

  @override
  ConsumerState<ClassesScreen> createState() => _ClassesScreenState();
}

class _ClassesScreenState extends ConsumerState<ClassesScreen> {
  final Set<String> _busy = {};

  Future<void> _toggleReservation(ClassSession session) async {
    if (_busy.contains(session.id)) return;
    setState(() => _busy.add(session.id));
    try {
      final repository = ref.read(classRepositoryProvider);
      if (session.isReserved) {
        await repository.cancel(session.id);
      } else {
        await repository.reserve(session.id);
      }
      ref.invalidate(classesProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              session.isReserved
                  ? 'Reservation cancelled.'
                  : 'Reservation confirmed for ${session.name}!',
            ),
            backgroundColor: session.isReserved ? Colors.red : Colors.green,
          ),
        );
      }
    } on ApiException catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(error.message), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _busy.remove(session.id));
    }
  }

  @override
  Widget build(BuildContext context) {
    final classes = ref.watch(classesProvider);
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'BOOK A CLASS',
          style: GoogleFonts.oswald(fontWeight: FontWeight.bold),
        ),
      ),
      body: classes.when(
        loading: () => const AsyncLoadingView(),
        error: (error, _) => AsyncErrorView(
          error: error,
          onRetry: () => ref.invalidate(classesProvider),
        ),
        data: (sessions) => RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(classesProvider);
            await ref.read(classesProvider.future);
          },
          child: ListView.builder(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(20),
            itemCount: sessions.length,
            itemBuilder: (context, index) {
              final session = sessions[index];
              final busy = _busy.contains(session.id);
              return Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: BrawlerzCard(
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              session.name.toUpperCase(),
                              style: GoogleFonts.oswald(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              '${DateFormat('EEE, MMM d').format(session.startTime.toLocal())} | ${DateFormat('h:mm a').format(session.startTime.toLocal())}',
                              style: TextStyle(
                                color: Colors.grey[400],
                                fontSize: 13,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'with ${session.trainer}',
                              style: TextStyle(
                                color: Colors.grey[500],
                                fontSize: 12,
                              ),
                            ),
                            if (session.capacity > 0)
                              Text(
                                '${session.reservedCount}/${session.capacity} reserved',
                                style: TextStyle(
                                  color: Colors.grey[600],
                                  fontSize: 11,
                                ),
                              ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 16),
                      SizedBox(
                        width: 105,
                        child: ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: session.isReserved
                                ? Colors.grey[800]
                                : const Color(0xFFFF4500),
                            padding: const EdgeInsets.symmetric(vertical: 12),
                          ),
                          onPressed: busy ? null : () => _toggleReservation(session),
                          child: busy
                              ? const SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                )
                              : Text(
                                  session.isReserved ? 'BOOKED' : 'RESERVE',
                                  style: const TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
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
