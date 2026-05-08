import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:brawlerz_box/shared/widgets/brawlerz_card.dart';
import 'package:brawlerz_box/shared/repositories/class_repository.dart';
import 'package:brawlerz_box/shared/models/class_session.dart';
import 'package:brawlerz_box/features/classes/classes_provider.dart';

class ClassesScreen extends ConsumerWidget {
  const ClassesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final classes = ref.watch(classRepositoryProvider).getClasses();
    final bookedClasses = ref.watch(bookedClassesProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(
          'BOOK A CLASS',
          style: GoogleFonts.oswald(fontWeight: FontWeight.bold),
        ),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(20),
        itemCount: classes.length,
        itemBuilder: (context, index) {
          final session = classes[index];
          final isReserved = bookedClasses.contains(session.id);
          final dateFormat = DateFormat('EEE, MMM d');
          final timeFormat = DateFormat('h:mm a');

          return Padding(
            padding: const EdgeInsets.bottom(16.0),
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
                          '${dateFormat.format(session.startTime)} | ${timeFormat.format(session.startTime)}',
                          style: TextStyle(color: Colors.grey[400], fontSize: 13),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'with ${session.trainer}',
                          style: TextStyle(color: Colors.grey[500], fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 16),
                  SizedBox(
                    width: 100,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: isReserved ? Colors.grey[800] : const Color(0xFFFF4500),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      onPressed: () {
                        ref.read(bookedClassesProvider.notifier).toggleBooking(session.id);
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(
                              !isReserved
                                ? 'Reservation confirmed for ${session.name}!'
                                : 'Reservation cancelled.',
                            ),
                            backgroundColor: !isReserved ? Colors.green : Colors.red,
                            duration: const Duration(seconds: 2),
                          ),
                        );
                      },
                      child: Text(
                        isReserved ? 'BOOKED' : 'RESERVE',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
