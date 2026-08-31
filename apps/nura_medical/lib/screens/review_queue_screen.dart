import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/models/models.dart';
import '../core/providers.dart';
import '../core/repositories/review_repository.dart';
import '../widgets/clinical_draft_view.dart';

final reviewRepositoryProvider = Provider<ReviewRepository>(
  (ref) => ReviewRepository(ref.watch(apiClientProvider)),
);

class ReviewQueueScreen extends ConsumerStatefulWidget {
  const ReviewQueueScreen({super.key});

  @override
  ConsumerState<ReviewQueueScreen> createState() => _ReviewQueueScreenState();
}

class _ReviewQueueScreenState extends ConsumerState<ReviewQueueScreen> {
  List<ClinicalDraft> _drafts = const [];
  ClinicalDraft? _selected;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final rows = await ref.read(reviewRepositoryProvider).queue();
      if (mounted) {
        setState(() {
          _drafts = rows;
          if (_selected != null) {
            _selected = rows.cast<ClinicalDraft?>().firstWhere(
                  (item) => item?.id == _selected!.id,
                  orElse: () => null,
                );
          }
        });
      }
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _review(ClinicalDraft draft, String status) async {
    final comment = TextEditingController();
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: Text(status == 'approved' ? 'Approve draft?' : 'Reject draft?'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              status == 'approved'
                  ? 'Approval records your independent clinician review. Verify the source facts, dangerous alternatives, missing data, and proposed next step before continuing.'
                  : 'Rejection prevents the draft from being represented as reviewed. Add the reason or required correction.',
            ),
            const SizedBox(height: 14),
            TextField(
              controller: comment,
              minLines: 2,
              maxLines: 6,
              decoration: InputDecoration(
                labelText: status == 'approved'
                    ? 'Review comment (optional)'
                    : 'Reason for rejection',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            style: status == 'rejected'
                ? FilledButton.styleFrom(backgroundColor: Colors.red)
                : null,
            onPressed: () => Navigator.pop(dialogContext, true),
            child: Text(status == 'approved' ? 'Approve' : 'Reject'),
          ),
        ],
      ),
    );
    if (confirmed != true) {
      comment.dispose();
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final updated = await ref.read(reviewRepositoryProvider).review(
            draftId: draft.id,
            status: status,
            comment: comment.text,
          );
      if (mounted) {
        setState(() {
          _selected = updated;
          _drafts = [
            for (final item in _drafts) if (item.id == updated.id) updated else item,
          ];
        });
      }
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    } finally {
      comment.dispose();
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final pending = _drafts.where((item) => item.status == 'draft').toList();
    return Scaffold(
      appBar: AppBar(
        title: const Text('Clinical Review Queue'),
        actions: [
          IconButton(
            onPressed: _loading ? null : _load,
            tooltip: 'Refresh',
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: _selected == null ? _queueBody(pending) : _detailBody(_selected!),
    );
  }

  Widget _queueBody(List<ClinicalDraft> pending) => RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.verified_user_outlined, color: Color(0xFF087F8C)),
                        SizedBox(width: 8),
                        Text(
                          'Independent clinical review required',
                          style: TextStyle(fontWeight: FontWeight.w800),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Approval is an accountable clinician action. Confirm source-fact fidelity, uncertainty, dangerous alternatives, missing information, and the proposed next step. Do not approve solely because the draft is fluent.',
                    ),
                    const SizedBox(height: 12),
                    Chip(label: Text('${pending.length} pending draft(s)')),
                  ],
                ),
              ),
            ),
            if (_error != null) ...[
              const SizedBox(height: 12),
              _errorBanner(_error!),
            ],
            const SizedBox(height: 14),
            if (_loading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(30),
                  child: CircularProgressIndicator(),
                ),
              )
            else if (pending.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(20),
                  child: Text('No drafts are awaiting clinical review.'),
                ),
              )
            else
              for (final draft in pending)
                Card(
                  child: ListTile(
                    leading: const CircleAvatar(child: Icon(Icons.edit_note)),
                    title: Text(
                      '${draft.operation.toUpperCase()} · ${draft.output.urgency.toUpperCase()}',
                      style: const TextStyle(fontWeight: FontWeight.w800),
                    ),
                    subtitle: Text(
                      '${draft.createdAt.toLocal()}\n${draft.output.interpretation}',
                      maxLines: 3,
                      overflow: TextOverflow.ellipsis,
                    ),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => setState(() => _selected = draft),
                  ),
                ),
            const SizedBox(height: 100),
          ],
        ),
      );

  Widget _detailBody(ClinicalDraft draft) => ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Align(
            alignment: Alignment.centerLeft,
            child: TextButton.icon(
              onPressed: () => setState(() => _selected = null),
              icon: const Icon(Icons.arrow_back),
              label: const Text('Back to queue'),
            ),
          ),
          if (_error != null) ...[
            _errorBanner(_error!),
            const SizedBox(height: 12),
          ],
          ClinicalDraftView(draft: draft),
          const SizedBox(height: 14),
          if (draft.status == 'draft')
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(foregroundColor: Colors.red),
                    onPressed: _loading ? null : () => _review(draft, 'rejected'),
                    icon: const Icon(Icons.cancel_outlined),
                    label: const Text('Reject'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: FilledButton.icon(
                    onPressed: _loading ? null : () => _review(draft, 'approved'),
                    icon: const Icon(Icons.verified_outlined),
                    label: const Text('Approve'),
                  ),
                ),
              ],
            ),
          const SizedBox(height: 100),
        ],
      );

  Widget _errorBanner(String message) => Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.errorContainer,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(message),
      );
}
