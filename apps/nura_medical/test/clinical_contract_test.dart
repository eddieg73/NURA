import 'package:flutter_test/flutter_test.dart';
import 'package:nura_medical/core/config/app_config.dart';
import 'package:nura_medical/core/models/models.dart';

void main() {
  test('clinical draft contract preserves safety fields', () {
    final draft = ClinicalDraft.fromJson({
      'id': 'draft-1',
      'encounter_id': 'encounter-1',
      'operation': 'synthesis',
      'provider_name': 'disabled-safe-mode',
      'model_name': null,
      'status': 'draft',
      'created_at': '2026-08-31T00:00:00Z',
      'provider_approval_required': true,
      'output': {
        'source_facts': ['Source fact'],
        'interpretation': 'Draft interpretation',
        'differential': [
          {
            'label': 'Option A',
            'support': 'Limited supplied evidence',
            'confidence': 'low',
          }
        ],
        'dangerous_alternatives': ['Dangerous alternative'],
        'red_flags': ['Red flag'],
        'missing_data': ['Missing vital signs'],
        'recommended_next_step': 'Clinician review',
        'urgency': 'undetermined',
        'confidence': 'low',
        'evidence_as_of': '2026-08-31',
        'limitations': ['Not autonomous'],
        'provenance': [],
      },
    });

    expect(draft.status, 'draft');
    expect(draft.providerApprovalRequired, isTrue);
    expect(draft.output.sourceFacts, ['Source fact']);
    expect(draft.output.dangerousAlternatives, isNotEmpty);
    expect(draft.output.missingData, isNotEmpty);
    expect(draft.output.confidence, 'low');
  });

  test('user contract parses organization and role', () {
    final user = AppUser.fromJson({
      'id': 'user-1',
      'organization_id': 'org-1',
      'email': 'clinician@example.com',
      'full_name': 'Clinical Reviewer',
      'role': 'reviewer',
      'active': true,
    });
    expect(user.organizationId, 'org-1');
    expect(user.role, 'reviewer');
    expect(user.active, isTrue);
  });

  test('API endpoint construction uses the configured origin', () {
    final endpoint = AppConfig.endpoint('/api/v1/legal');
    expect(endpoint.path, '/api/v1/legal');
    expect(endpoint.hasScheme, isTrue);
  });
}
