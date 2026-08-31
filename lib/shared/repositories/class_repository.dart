import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:brawlerz_box/core/api/api_client.dart';
import 'package:brawlerz_box/shared/models/class_session.dart';

abstract class IClassRepository {
  Future<List<ClassSession>> getClasses();
  Future<ClassSession> reserve(String classId);
  Future<ClassSession> cancel(String classId);
}

class ClassRepository implements IClassRepository {
  final ApiClient _api;

  ClassRepository(this._api);

  @override
  Future<List<ClassSession>> getClasses() async {
    final payload = await _api.request('GET', '/api/v1/classes') as List;
    return payload
        .whereType<Map>()
        .map((item) => ClassSession.fromJson(
              Map<String, dynamic>.from(item),
            ))
        .toList(growable: false);
  }

  @override
  Future<ClassSession> reserve(String classId) async {
    final payload = await _api.request(
      'POST',
      '/api/v1/classes/$classId/reserve',
    ) as Map<String, dynamic>;
    return ClassSession.fromJson(payload);
  }

  @override
  Future<ClassSession> cancel(String classId) async {
    final payload = await _api.request(
      'DELETE',
      '/api/v1/classes/$classId/reserve',
    ) as Map<String, dynamic>;
    return ClassSession.fromJson(payload);
  }
}

final classRepositoryProvider = Provider<IClassRepository>((ref) {
  return ClassRepository(ref.watch(apiClientProvider));
});

final classesProvider = FutureProvider<List<ClassSession>>((ref) {
  return ref.watch(classRepositoryProvider).getClasses();
});
