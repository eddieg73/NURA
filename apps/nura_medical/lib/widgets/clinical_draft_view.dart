import 'package:flutter/material.dart';

import '../core/models/models.dart';

class ClinicalDraftView extends StatelessWidget {
  const ClinicalDraftView({super.key, required this.draft});

  final ClinicalDraft draft;

  @override
  Widget build(BuildContext context) {
    final output = draft.output;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _statusBanner(context),
        const SizedBox(height: 12),
        _section(
          context,
          title: 'Source facts',
          icon: Icons.fact_check_outlined,
          children: output.sourceFacts,
        ),
        _textSection(
          context,
          title: 'Interpretation',
          icon: Icons.psychology_alt_outlined,
          text: output.interpretation,
        ),
        if (output.differential.isNotEmpty)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _heading(Icons.format_list_numbered, 'Ordered possibilities'),
                  const SizedBox(height: 10),
                  for (final item in output.differential)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 10),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: Text(
                                  item.label,
                                  style: const TextStyle(fontWeight: FontWeight.w700),
                                ),
                              ),
                              _chip(item.confidence),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(item.support),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          ),
        _section(
          context,
          title: 'Dangerous alternatives',
          icon: Icons.warning_amber_rounded,
          children: output.dangerousAlternatives,
          emptyText: 'None supplied by the draft engine.',
        ),
        _section(
          context,
          title: 'Red flags',
          icon: Icons.emergency_outlined,
          children: output.redFlags,
          emptyText: 'No red flags were identified in the submitted text.',
        ),
        _section(
          context,
          title: 'Missing data',
          icon: Icons.help_outline,
          children: output.missingData,
          emptyText: 'No missing-data items were supplied.',
        ),
        _textSection(
          context,
          title: 'Recommended next step',
          icon: Icons.next_plan_outlined,
          text: output.recommendedNextStep,
        ),
        _section(
          context,
          title: 'Limitations',
          icon: Icons.gpp_maybe_outlined,
          children: output.limitations,
        ),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Wrap(
              spacing: 10,
              runSpacing: 8,
              children: [
                _chip('Urgency: ${output.urgency}'),
                _chip('Confidence: ${output.confidence}'),
                _chip('Evidence date: ${output.evidenceAsOf}'),
                _chip('Provider: ${draft.providerName}'),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _statusBanner(BuildContext context) {
    final approved = draft.status == 'approved';
    final rejected = draft.status == 'rejected';
    final color = approved
        ? Colors.green
        : rejected
            ? Colors.red
            : Colors.orange;
    return Semantics(
      liveRegion: true,
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.12),
          border: Border.all(color: color.withValues(alpha: 0.5)),
          borderRadius: BorderRadius.circular(14),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              approved
                  ? Icons.verified_outlined
                  : rejected
                      ? Icons.cancel_outlined
                      : Icons.edit_note,
              color: color,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                approved
                    ? 'Clinician-reviewed and approved.'
                    : rejected
                        ? 'Rejected during clinician review.'
                        : 'DRAFT — accountable clinician approval is required before use.',
                style: TextStyle(
                  color: color.shade700,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _section(
    BuildContext context, {
    required String title,
    required IconData icon,
    required List<String> children,
    String emptyText = 'No items supplied.',
  }) =>
      Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _heading(icon, title),
              const SizedBox(height: 10),
              if (children.isEmpty)
                Text(emptyText, style: Theme.of(context).textTheme.bodySmall)
              else
                for (final item in children)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 7),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('•  '),
                        Expanded(child: Text(item)),
                      ],
                    ),
                  ),
            ],
          ),
        ),
      );

  Widget _textSection(
    BuildContext context, {
    required String title,
    required IconData icon,
    required String text,
  }) =>
      Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _heading(icon, title),
              const SizedBox(height: 10),
              SelectableText(text),
            ],
          ),
        ),
      );

  Widget _heading(IconData icon, String title) => Row(
        children: [
          Icon(icon, size: 20, color: const Color(0xFF087F8C)),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              title,
              style: const TextStyle(fontWeight: FontWeight.w800),
            ),
          ),
        ],
      );

  Widget _chip(String text) => Chip(
        visualDensity: VisualDensity.compact,
        label: Text(text, style: const TextStyle(fontSize: 12)),
      );
}
