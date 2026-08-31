import '../models/models.dart';
import '../network/api_client.dart';

class ReviewRepository {
  const ReviewRepository(this._api);

  final ApiClient _api;

  Future<List<ClinicalDraft>> queue() async {
    final response = await _api.get('/api/v1/clinical/drafts');
    if (response is! List) return const [];
    return response
        .whereType<Map>()
        .map((item) => ClinicalDraft.fromJson(
              Map<String, dynamic>.from(item),
            ))
        .toList(growable: false);
  }

  Future<ClinicalDraft> review({
    required String draftId,
    required String status,
    String? comment,
  }) async {
    final response = await _api.post(
      '/api/v1/clinical/drafts/$draftId/review',
      body: {
        'status': status,
        'comment': comment?.trim().isEmpty == true ? null : comment?.trim(),
      },
    );
    if (response is! Map<String, dynamic>) {
      throw const ApiException('The review response was invalid.');
    }
    return ClinicalDraft.fromJson(response);
  }
}
