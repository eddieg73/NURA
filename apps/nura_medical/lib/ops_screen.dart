import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/models/models.dart';
import 'core/providers.dart';

class OpsScreen extends ConsumerStatefulWidget {
  const OpsScreen({super.key});

  @override
  ConsumerState<OpsScreen> createState() => _OpsScreenState();
}

class _OpsScreenState extends ConsumerState<OpsScreen> {
  List<OpsTask> _tasks = const [];
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
      final tasks = await ref.read(opsRepositoryProvider).listTasks();
      if (mounted) setState(() => _tasks = tasks);
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _createTask() async {
    final title = TextEditingController();
    final detail = TextEditingController();
    String priority = 'normal';
    final accepted = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('New operations task'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: title,
                  autofocus: true,
                  decoration: const InputDecoration(labelText: 'Task title'),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: detail,
                  minLines: 2,
                  maxLines: 6,
                  decoration: const InputDecoration(labelText: 'Detail'),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  initialValue: priority,
                  decoration: const InputDecoration(labelText: 'Priority'),
                  items: const [
                    DropdownMenuItem(value: 'low', child: Text('Low')),
                    DropdownMenuItem(value: 'normal', child: Text('Normal')),
                    DropdownMenuItem(value: 'high', child: Text('High')),
                    DropdownMenuItem(value: 'urgent', child: Text('Urgent')),
                  ],
                  onChanged: (value) =>
                      setDialogState(() => priority = value ?? 'normal'),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogContext, false),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(dialogContext, true),
              child: const Text('Create'),
            ),
          ],
        ),
      ),
    );
    if (accepted != true || title.text.trim().isEmpty) {
      title.dispose();
      detail.dispose();
      return;
    }
    try {
      final created = await ref.read(opsRepositoryProvider).createTask(
            title: title.text.trim(),
            detail: detail.text.trim().isEmpty ? null : detail.text.trim(),
            priority: priority,
          );
      if (mounted) setState(() => _tasks = [created, ..._tasks]);
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    } finally {
      title.dispose();
      detail.dispose();
    }
  }

  Future<void> _toggle(OpsTask task) async {
    final next = task.status == 'completed' ? 'open' : 'completed';
    try {
      final updated =
          await ref.read(opsRepositoryProvider).setStatus(task.id, next);
      if (mounted) {
        setState(() {
          _tasks = [
            for (final item in _tasks) if (item.id == updated.id) updated else item,
          ];
        });
      }
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('NURA Operations'),
        actions: [
          IconButton(
            onPressed: _loading ? null : _load,
            tooltip: 'Refresh',
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _createTask,
        icon: const Icon(Icons.add_task),
        label: const Text('Task'),
      ),
      body: RefreshIndicator(
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
                        Icon(Icons.shield_outlined, color: Color(0xFF087F8C)),
                        SizedBox(width: 8),
                        Text(
                          'Controlled operations lane',
                          style: TextStyle(fontWeight: FontWeight.w800),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Tasks are stored in the organization-scoped backend. Email, SMS, fax, payment, and EHR connectors remain disabled until each service is approved, authenticated, and audited.',
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: const [
                        Chip(label: Text('Tasks · active')),
                        Chip(label: Text('Messaging · gated')),
                        Chip(label: Text('Fax · gated')),
                        Chip(label: Text('Payments · gated')),
                        Chip(label: Text('EHR · gated')),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            if (_error != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.errorContainer,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(_error!),
              ),
            ],
            const SizedBox(height: 14),
            Text(
              'My task queue',
              style: Theme.of(context)
                  .textTheme
                  .titleLarge
                  ?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 8),
            if (_loading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(30),
                  child: CircularProgressIndicator(),
                ),
              )
            else if (_tasks.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(20),
                  child: Text('No operations tasks are assigned.'),
                ),
              )
            else
              for (final task in _tasks)
                Card(
                  child: CheckboxListTile(
                    value: task.status == 'completed',
                    onChanged: (_) => _toggle(task),
                    controlAffinity: ListTileControlAffinity.leading,
                    title: Text(
                      task.title,
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        decoration: task.status == 'completed'
                            ? TextDecoration.lineThrough
                            : null,
                      ),
                    ),
                    subtitle: Text(
                      [
                        task.priority.toUpperCase(),
                        task.status.replaceAll('_', ' ').toUpperCase(),
                        if (task.detail?.isNotEmpty == true) task.detail!,
                      ].join(' · '),
                    ),
                  ),
                ),
            const SizedBox(height: 100),
          ],
        ),
      ),
    );
  }
}
