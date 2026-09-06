import 'package:flutter/material.dart';

const String kApiBase = String.fromEnvironment('CAREPILOT_API', defaultValue: 'http://localhost:8000');

/// Home screen — the Work Queue (unified work-queue per spec #10).
/// Every item has owner, due date, next action, evidence; status flow New→In Progress→Completed/Escalated.
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('CarePilot — Work Queue')),
      body: const WorkQueueView(),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Task creation is RBAC-gated (provider/nurse roles only.')),
        ),
        icon: const Icon(Icons.add),
        label: const Text('New Task'),
      ),
    );
  }
}

class WorkQueueView extends StatelessWidget {
  const WorkQueueView({super.key});
  @override
  Widget build(BuildContext context) {
    // Demo rows (P0); wired to GET /api/work-queue in P1 via package:http.
    final tasks = [
      _DemoTask('Close HbA1c care gap', 'nurse-1', 'Next', 'Order A1c', 'HEDIS'),
      _DemoTask('CCM monthly — patient P0001', 'provider-1', 'In Progress', 'Call + care-time log', 'CCM'),
      _DemoTask('Med safety reconciliation', 'cpa', 'New', 'Review ordered vs dispensed', 'Safety'),
    ];
    return ListView.separated(
      padding: const EdgeInsets.all(12),
      itemCount: tasks.length,
      separatorBuilder: (_, __) => const Divider(height: 8),
      itemBuilder: (_, i) {
        final t = tasks[i];
        return Card(
          child: ListTile(
            leading: const Icon(Icons.task_alt),
            title: Text(t.title),
            subtitle: Text('${t.category} · owner ${t.owner} · next: ${t.nextAction}'),
            trailing: Chip(label: Text(t.status)),
            onTap: () => ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('Drill list: ${t.title} (owners, due, evidence)')),
            ),
          ),
        );
      },
    );
  }
}

class _DemoTask {
  const _DemoTask(this.title, this.owner, this.status, this.nextAction, this.category);
  final String title, owner, status, nextAction, category;
}
