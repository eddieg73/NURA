class UserMetrics {
  final int readinessScore;
  final int hrv;
  final int sleepScore;
  final int recoveryPercentage;
  final List<ProgressDataPoint> strengthHistory;
  final List<ProgressDataPoint> weightHistory;

  const UserMetrics({
    required this.readinessScore,
    required this.hrv,
    required this.sleepScore,
    required this.recoveryPercentage,
    required this.strengthHistory,
    required this.weightHistory,
  });

  factory UserMetrics.fromJson(Map<String, dynamic> json) {
    return UserMetrics(
      readinessScore: (json['readinessScore'] as num?)?.toInt() ?? 0,
      hrv: (json['hrv'] as num?)?.toInt() ?? 0,
      sleepScore: (json['sleepScore'] as num?)?.toInt() ?? 0,
      recoveryPercentage:
          (json['recoveryPercentage'] as num?)?.toInt() ?? 0,
      strengthHistory: _points(json['strengthHistory']),
      weightHistory: _points(json['weightHistory']),
    );
  }

  static List<ProgressDataPoint> _points(dynamic raw) {
    if (raw is! List) return const [];
    return raw
        .whereType<Map>()
        .map((item) => ProgressDataPoint.fromJson(
              Map<String, dynamic>.from(item),
            ))
        .toList(growable: false);
  }
}

class ProgressDataPoint {
  final double x;
  final double y;

  const ProgressDataPoint(this.x, this.y);

  factory ProgressDataPoint.fromJson(Map<String, dynamic> json) {
    return ProgressDataPoint(
      (json['x'] as num?)?.toDouble() ?? 0,
      (json['y'] as num?)?.toDouble() ?? 0,
    );
  }
}
