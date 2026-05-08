import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:brawlerz_box/shared/models/class_session.dart';

abstract class IClassRepository {
  List<ClassSession> getClasses();
}

class ClassRepository implements IClassRepository {
  @override
  List<ClassSession> getClasses() {
    // TODO: Integrate with Gym Management API (e.g. Mindbody)
    final now = DateTime.now();
    return [
      ClassSession(
        id: '1',
        name: 'Boxing Fundamentals',
        trainer: 'Coach Mike',
        startTime: DateTime(now.year, now.month, now.day + 1, 18, 0),
        durationMinutes: 60,
      ),
      ClassSession(
        id: '2',
        name: 'HIIT Training',
        trainer: 'Coach Sarah',
        startTime: DateTime(now.year, now.month, now.day + 2, 9, 0),
        durationMinutes: 45,
      ),
      ClassSession(
        id: '3',
        name: 'MMA Conditioning',
        trainer: 'Coach Alex',
        startTime: DateTime(now.year, now.month, now.day + 3, 17, 30),
        durationMinutes: 90,
      ),
      ClassSession(
        id: '4',
        name: 'Personal Training',
        trainer: 'Coach Elena',
        startTime: DateTime(now.year, now.month, now.day + 4, 13, 0),
        durationMinutes: 60,
      ),
    ];
  }
}

final classRepositoryProvider = Provider<IClassRepository>((ref) => ClassRepository());
