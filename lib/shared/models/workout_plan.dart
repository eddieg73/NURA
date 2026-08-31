class WorkoutPlan {
  final String id;
  final String title;
  final String description;
  final String level;
  final String duration;
  final String imageUrl;
  final String category;

  const WorkoutPlan({
    required this.id,
    required this.title,
    required this.description,
    required this.level,
    required this.duration,
    required this.imageUrl,
    required this.category,
  });

  factory WorkoutPlan.fromJson(Map<String, dynamic> json) {
    return WorkoutPlan(
      id: json['id'].toString(),
      title: json['title'] as String? ?? '',
      description: json['description'] as String? ?? '',
      level: json['level'] as String? ?? '',
      duration: json['duration'] as String? ?? '',
      imageUrl: json['imageUrl'] as String? ?? '',
      category: json['category'] as String? ?? '',
    );
  }
}
