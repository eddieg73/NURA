import 'package:flutter/material.dart';
import '../api.dart';

/// Unified Work Queue — every task has owner/due/next-action/evidence; status flow New→InProgress→Completed/Escalated.
class WorkQueueScreen extends StatefulWidget {
  const WorkQueueScreen({super.key});
  @override State<WorkQueueScreen> createState() => _WorkQueueScreenState();
}
class _WorkQueueScreenState extends State<WorkQueueScreen> {
  List<dynamic> _tasks = []; String _err='';
  @override void initState() { super.initState(); _load(); }
  Future<void> _load() async {
    try { final d = await Api.get('/api/work-queue'); setState(() { _tasks = (d['tasks'] as List?) ?? []; _err=''; }); }
    catch(e){ setState(()=>_err=e.toString()); }
  }
  Future<void> _create() async {
    Api.role='provider';
    try { await Api.post('/api/tasks', {'source':'P1','task_type':'gap','title':'New follow-up','owner':'nurse-1'}); _load(); }
    catch(e){ setState(()=>_err=e.toString()); }
  }
  @override Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: const Text('Work Queue')),
      body: _err!='' ? Center(child: Text('Backend: $_err'))
        : ListView.separated(padding: const EdgeInsets.all(8), itemCount: _tasks.length,
          separatorBuilder:(_,__)=>const Divider(height:4),
          itemBuilder:(_,i){ final t=_tasks[i]; return Card(child: ListTile(
            leading: const Icon(Icons.task_alt),
            title: Text(t['title'] ?? ''),
            subtitle: Text('${t['task_type']} · owner ${t['owner']} · ${t['next_action']}'),
            trailing: Chip(label: Text(t['status'] ?? 'New')),
            onTap: ()=>ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Assignee/due/evidence for ${t['title']}'))),
          )); }),
      floatingActionButton: FloatingActionButton.extended(onPressed: _create, icon: const Icon(Icons.add), label: const Text('New Task')));
  }
}
