class ClassSession {
  final String id;
  final String name;
  final DateTime startTime;
  final String trainer;
  final int durationMinutes;
  final bool isReserved;

  ClassSession({
    required this.id,
    required this.name,
    required this.startTime,
    required this.trainer,
    required this.durationMinutes,
    this.isReserved = false,
  });

  ClassSession copyWith({bool? isReserved}) {
    return ClassSession(
      id: id,
      name: name,
      startTime: startTime,
      trainer: trainer,
      durationMinutes: durationMinutes,
      isReserved: isReserved ?? this.isReserved,
    );
  }
}
