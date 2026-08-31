class AppUser {
  const AppUser({
    required this.id,
    required this.organizationId,
    required this.email,
    required this.fullName,
    required this.role,
    required this.active,
  });

  final String id;
  final String organizationId;
  final String email;
  final String fullName;
  final String role;
  final bool active;

  factory AppUser.fromJson(Map<String, dynamic> json) => AppUser(
        id: json['id'] as String,
        organizationId: json['organization_id'] as String,
        email: json['email'] as String,
        fullName: json['full_name'] as String,
        role: json['role'] as String,
        active: json['active'] as bool? ?? true,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'organization_id': organizationId,
        'email': email,
        'full_name': fullName,
        'role': role,
        'active': active,
      };
}

class SessionData {
  const SessionData({
    required this.accessToken,
    required this.refreshToken,
    required this.user,
  });

  final String accessToken;
  final String refreshToken;
  final AppUser user;

  factory SessionData.fromJson(Map<String, dynamic> json) => SessionData(
        accessToken: json['access_token'] as String,
        refreshToken: json['refresh_token'] as String,
        user: AppUser.fromJson(
          Map<String, dynamic>.from(json['user'] as Map),
        ),
      );
}

class DifferentialItem {
  const DifferentialItem({
    required this.label,
    required this.support,
    required this.confidence,
  });

  final String label;
  final String support;
  final String confidence;

  factory DifferentialItem.fromJson(Map<String, dynamic> json) =>
      DifferentialItem(
        label: json['label'] as String? ?? 'Unspecified',
        support: json['support'] as String? ?? '',
        confidence: json['confidence'] as String? ?? 'low',
      );
}

class ClinicalOutput {
  const ClinicalOutput({
    required this.sourceFacts,
    required this.interpretation,
    required this.differential,
    required this.dangerousAlternatives,
    required this.redFlags,
    required this.missingData,
    required this.recommendedNextStep,
    required this.urgency,
    required this.confidence,
    required this.evidenceAsOf,
    required this.limitations,
  });

  final List<String> sourceFacts;
  final String interpretation;
  final List<DifferentialItem> differential;
  final List<String> dangerousAlternatives;
  final List<String> redFlags;
  final List<String> missingData;
  final String recommendedNextStep;
  final String urgency;
  final String confidence;
  final String evidenceAsOf;
  final List<String> limitations;

  factory ClinicalOutput.fromJson(Map<String, dynamic> json) => ClinicalOutput(
        sourceFacts: _stringList(json['source_facts']),
        interpretation: json['interpretation'] as String? ?? '',
        differential: (json['differential'] as List? ?? const [])
            .whereType<Map>()
            .map((item) => DifferentialItem.fromJson(
                  Map<String, dynamic>.from(item),
                ))
            .toList(),
        dangerousAlternatives: _stringList(json['dangerous_alternatives']),
        redFlags: _stringList(json['red_flags']),
        missingData: _stringList(json['missing_data']),
        recommendedNextStep: json['recommended_next_step'] as String? ?? '',
        urgency: json['urgency'] as String? ?? 'undetermined',
        confidence: json['confidence'] as String? ?? 'low',
        evidenceAsOf: json['evidence_as_of'] as String? ?? '',
        limitations: _stringList(json['limitations']),
      );
}

class ClinicalDraft {
  const ClinicalDraft({
    required this.id,
    required this.encounterId,
    required this.operation,
    required this.output,
    required this.providerName,
    required this.modelName,
    required this.status,
    required this.createdAt,
    required this.providerApprovalRequired,
    this.reviewedBy,
    this.reviewedAt,
    this.reviewComment,
  });

  final String id;
  final String encounterId;
  final String operation;
  final ClinicalOutput output;
  final String providerName;
  final String? modelName;
  final String status;
  final DateTime createdAt;
  final bool providerApprovalRequired;
  final String? reviewedBy;
  final DateTime? reviewedAt;
  final String? reviewComment;

  factory ClinicalDraft.fromJson(Map<String, dynamic> json) => ClinicalDraft(
        id: json['id'] as String,
        encounterId: json['encounter_id'] as String,
        operation: json['operation'] as String,
        output: ClinicalOutput.fromJson(
          Map<String, dynamic>.from(json['output'] as Map),
        ),
        providerName: json['provider_name'] as String? ?? 'unknown',
        modelName: json['model_name'] as String?,
        status: json['status'] as String? ?? 'draft',
        createdAt: DateTime.tryParse(json['created_at'] as String? ?? '') ??
            DateTime.fromMillisecondsSinceEpoch(0, isUtc: true),
        providerApprovalRequired:
            json['provider_approval_required'] as bool? ?? true,
        reviewedBy: json['reviewed_by'] as String?,
        reviewedAt: DateTime.tryParse(json['reviewed_at'] as String? ?? ''),
        reviewComment: json['review_comment'] as String?,
      );
}

class OpsTask {
  const OpsTask({
    required this.id,
    required this.title,
    required this.detail,
    required this.status,
    required this.priority,
    required this.createdAt,
    this.completedAt,
  });

  final String id;
  final String title;
  final String? detail;
  final String status;
  final String priority;
  final DateTime createdAt;
  final DateTime? completedAt;

  factory OpsTask.fromJson(Map<String, dynamic> json) => OpsTask(
        id: json['id'] as String,
        title: json['title'] as String,
        detail: json['detail'] as String?,
        status: json['status'] as String? ?? 'open',
        priority: json['priority'] as String? ?? 'normal',
        createdAt: DateTime.tryParse(json['created_at'] as String? ?? '') ??
            DateTime.fromMillisecondsSinceEpoch(0, isUtc: true),
        completedAt: DateTime.tryParse(json['completed_at'] as String? ?? ''),
      );
}

class LegalConfig {
  const LegalConfig({
    required this.privacyPolicyUrl,
    required this.termsUrl,
    required this.supportUrl,
    required this.clinicalDisclaimer,
  });

  final String privacyPolicyUrl;
  final String termsUrl;
  final String supportUrl;
  final String clinicalDisclaimer;

  factory LegalConfig.fromJson(Map<String, dynamic> json) => LegalConfig(
        privacyPolicyUrl: json['privacy_policy_url'] as String? ?? '',
        termsUrl: json['terms_url'] as String? ?? '',
        supportUrl: json['support_url'] as String? ?? '',
        clinicalDisclaimer: json['clinical_disclaimer'] as String? ?? '',
      );
}

List<String> _stringList(dynamic value) =>
    (value as List? ?? const []).whereType<String>().toList(growable: false);
