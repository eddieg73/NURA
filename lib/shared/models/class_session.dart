class ClassSession {
  final String id;
  final String name;
  final DateTime startTime;
  final String trainer;
  final int durationMinutes;
  final bool isReserved;
  final int capacity;
  final int reservedCount;

  const ClassSession({
    required this.id,
    required this.name,
    required this.startTime,
    required this.trainer,
    required this.durationMinutes,
    this.isReserved = false,
    this.capacity = 0,
    this.reservedCount = 0,
  });

  factory ClassSession.fromJson(Map<String, dynamic> json) {
    return ClassSession(
      id: json['id'].toString(),
      name: json['name'] as String? ?? '',
      startTime: DateTime.parse(json['startTime'] as String),
      trainer: json['trainer'] as String? ?? '',
      durationMinutes: (json['durationMinutes'] as num?)?.toInt() ?? 0,
      isReserved: json['isReserved'] as bool? ?? false,
      capacity: (json['capacity'] as num?)?.toInt() ?? 0,
      reservedCount: (json['reservedCount'] as num?)?.toInt() ?? 0,
    );
  }

  ClassSession copyWith({bool? isReserved, int? reservedCount}) {
    return ClassSession(
      id: id,
      name: name,
      startTime: startTime,
      trainer: trainer,
      durationMinutes: durationMinutes,
      isReserved: isReserved ?? this.isReserved,
      capacity: capacity,
      reservedCount: reservedCount ?? this.reservedCount,
    );
  }
}
