import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:brawlerz_box/shared/models/user_metrics.dart';

abstract class IUserMetricsRepository {
  UserMetrics getUserMetrics();
}

class UserMetricsRepository implements IUserMetricsRepository {
  @override
  UserMetrics getUserMetrics() {
    // TODO: Connect to Wearable APIs (Apple Health, Garmin, WHOOP)
    return UserMetrics(
      readinessScore: 88,
      hrv: 65,
      sleepScore: 82,
      recoveryPercentage: 75,
      strengthHistory: [
        ProgressDataPoint(0, 100),
        ProgressDataPoint(1, 105),
        ProgressDataPoint(2, 103),
        ProgressDataPoint(3, 110),
        ProgressDataPoint(4, 115),
        ProgressDataPoint(5, 120),
        ProgressDataPoint(6, 125),
      ],
      weightHistory: [
        ProgressDataPoint(0, 85),
        ProgressDataPoint(1, 84.5),
        ProgressDataPoint(2, 84.2),
        ProgressDataPoint(3, 83.8),
        ProgressDataPoint(4, 83.5),
        ProgressDataPoint(5, 83.0),
        ProgressDataPoint(6, 82.5),
      ],
    );
  }
}

final userMetricsRepositoryProvider = Provider<IUserMetricsRepository>((ref) => UserMetricsRepository());
