class UserMetrics {
  final int readinessScore;
  final int hrv;
  final int sleepScore;
  final int recoveryPercentage;
  final List<ProgressDataPoint> strengthHistory;
  final List<ProgressDataPoint> weightHistory;

  UserMetrics({
    required this.readinessScore,
    required this.hrv,
    required this.sleepScore,
    required this.recoveryPercentage,
    required this.strengthHistory,
    required this.weightHistory,
  });
}

class ProgressDataPoint {
  final double x;
  final double y;

  ProgressDataPoint(this.x, this.y);
}
