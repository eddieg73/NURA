import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:brawlerz_box/shared/models/class_session.dart';
import 'package:brawlerz_box/shared/repositories/class_repository.dart';

final bookedClassesProvider = StateNotifierProvider<BookedClassesNotifier, List<String>>((ref) {
  return BookedClassesNotifier();
});

class BookedClassesNotifier extends StateNotifier<List<String>> {
  BookedClassesNotifier() : super([]);

  void toggleBooking(String classId) {
    if (state.contains(classId)) {
      state = state.where((id) => id != classId).toList();
    } else {
      state = [...state, classId];
    }
  }
}
