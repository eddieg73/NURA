import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/models/models.dart';
import 'core/providers.dart';
import 'widgets/clinical_draft_view.dart';

class ClinicalScreen extends ConsumerStatefulWidget {
  const ClinicalScreen({super.key});

  @override
  ConsumerState<ClinicalScreen> createState() => _ClinicalScreenState();
}

class _ClinicalScreenState extends ConsumerState<ClinicalScreen> {
  final _caseText = TextEditingController();
  final _patientReference = TextEditingController();
  String _operation = 'synthesis';
  bool _consent = false;
  bool _busy = false;
  String? _error;
  ClinicalDraft? _draft;
  List<ClinicalDraft> _history = const [];
  bool _showHistory = false;

  @override
  void dispose() {
    _caseText.dispose();
    _patientReference.dispose();
    super.dispose();
  }

  Future<void> _run() async {
    if (_caseText.text.trim().isEmpty) {
      setState(() => _error = 'Enter the clinical source text.');
      return;
    }
    if (!_consent) {
      setState(() => _error =
          'Confirm patient consent and your authority to submit this clinical information.');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
      _draft = null;
    });
    try {
      final draft = await ref.read(clinicalRepositoryProvider).createDraft(
            operation: _operation,
            caseText: _caseText.text.trim(),
            patientReference: _patientReference.text,
            consentAttested: _consent,
          );
      if (mounted) setState(() => _draft = draft);
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _loadHistory() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final history = await ref.read(clinicalRepositoryProvider).listDrafts();
      if (mounted) {
        setState(() {
          _history = history;
          _showHistory = true;
        });
      }
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('NURA Clinical'),
        actions: [
          IconButton(
            tooltip: 'Draft history',
            onPressed: _busy ? null : _loadHistory,
            icon: const Icon(Icons.history),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.red.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: Colors.red.withValues(alpha: 0.35)),
            ),
            child: const Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.emergency_outlined, color: Colors.red),
                SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Not for emergency communication. For an emergency, activate the appropriate emergency response system. '
                    'NURA output is decision-support draft material only.',
                    style: TextStyle(fontWeight: FontWeight.w700),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  SegmentedButton<String>(
                    segments: const [
                      ButtonSegment(
                        value: 'synthesis',
                        icon: Icon(Icons.hub_outlined),
                        label: Text('Synthesis'),
                      ),
                      ButtonSegment(
                        value: 'dx',
                        icon: Icon(Icons.manage_search),
                        label: Text('Differential'),
                      ),
                    ],
                    selected: {_operation},
                    onSelectionChanged: _busy
                        ? null
                        : (selection) =>
                            setState(() => _operation = selection.first),
                  ),
                  const SizedBox(height: 14),
                  TextField(
                    controller: _patientReference,
                    decoration: const InputDecoration(
                      labelText: 'Patient reference (minimum necessary)',
                      hintText: 'Prefer de-identified or internal reference',
                      prefixIcon: Icon(Icons.badge_outlined),
                    ),
                  ),
                  const SizedBox(height: 14),
                  TextField(
                    controller: _caseText,
                    minLines: 10,
                    maxLines: 24,
                    textCapitalization: TextCapitalization.sentences,
                    decoration: const InputDecoration(
                      labelText: 'Source facts: history, examination, tests, context',
                      alignLabelWithHint: true,
                      helperText:
                          'Do not paste more information than is necessary for the clinical purpose.',
                    ),
                  ),
                  SwitchListTile.adaptive(
                    contentPadding: EdgeInsets.zero,
                    value: _consent,
                    onChanged: _busy
                        ? null
                        : (value) => setState(() => _consent = value),
                    title: const Text('Consent and authority attested'),
                    subtitle: const Text(
                      'I am authorized to process this information for care or approved operations.',
                    ),
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: 8),
                    _errorBanner(context, _error!),
                  ],
                  const SizedBox(height: 12),
                  FilledButton.icon(
                    onPressed: _busy ? null : _run,
                    icon: _busy
                        ? const SizedBox.square(
                            dimension: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.auto_awesome),
                    label: Text(_busy
                        ? 'Running approved clinical lane…'
                        : _operation == 'dx'
                            ? 'Create differential draft'
                            : 'Create synthesis draft'),
                  ),
                ],
              ),
            ),
          ),
          if (_showHistory) ...[
            const SizedBox(height: 14),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Expanded(
                          child: Text(
                            'Recent drafts',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                        ),
                        IconButton(
                          onPressed: () => setState(() => _showHistory = false),
                          icon: const Icon(Icons.close),
                        ),
                      ],
                    ),
                    if (_history.isEmpty)
                      const Text('No drafts are available for this organization.')
                    else
                      for (final item in _history.take(20))
                        ListTile(
                          contentPadding: EdgeInsets.zero,
                          leading: Icon(
                            item.operation == 'dx'
                                ? Icons.manage_search
                                : Icons.hub_outlined,
                          ),
                          title: Text(
                            '${item.operation.toUpperCase()} · ${item.status.toUpperCase()}',
                          ),
                          subtitle: Text(
                            '${item.createdAt.toLocal()}\n${item.output.interpretation}',
                            maxLines: 3,
                            overflow: TextOverflow.ellipsis,
                          ),
                          onTap: () => setState(() {
                            _draft = item;
                            _showHistory = false;
                          }),
                        ),
                  ],
                ),
              ),
            ),
          ],
          const SizedBox(height: 14),
          if (_draft != null) ClinicalDraftView(draft: _draft!),
          const SizedBox(height: 80),
        ],
      ),
    );
  }

  Widget _errorBanner(BuildContext context, String message) => Semantics(
        liveRegion: true,
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.errorContainer,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            message,
            style: TextStyle(
              color: Theme.of(context).colorScheme.onErrorContainer,
            ),
          ),
        ),
      );
}
