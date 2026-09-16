import 'package:flutter/material.dart';
import '../api.dart';

/// Medication Safety Center — cross-check ordered/dispensed/given/billed.
/// Safety findings are NOT closable by AI; human clinical only. Safety override cost.
class MedSafetyScreen extends StatefulWidget {
  const MedSafetyScreen({super.key});
  @override State<MedSafetyScreen> createState() => _MedSafetyScreenState();
}
class _MedSafetyScreenState extends State<MedSafetyScreen> {
  List<dynamic> _alerts=[]; String _err='';
  @override void initState(){super.initState(); _load();}
  Future<void> _load() async {
    try { final d=await Api.get('/api/medication-alerts'); setState((){_alerts=(d['alerts'] as List?)??[]; _err='';}); }
    catch(e){ setState(()=>_err=e.toString()); }
  }
  @override Widget build(BuildContext context){
    return Scaffold(appBar: AppBar(title: const Text('Medication Safety')),
      body: _err!='' ? Center(child: Text('Backend: $_err'))
        : ListView.builder(padding: const EdgeInsets.all(8), itemCount:_alerts.length, itemBuilder:(_,i){
          final a=_alerts[i];
          final sev=a['severity']=='critical' ? Colors.red : Colors.orange;
          return Card(child: ListTile(
            leading: Icon(Icons.warning_amber, color: sev),
            title: Text(a['finding'] ?? ''),
            subtitle: Text('${a['type']} · ${a['status']}'),
            trailing: Chip(label: Text(a['severity'] ?? ''), backgroundColor: sev, labelStyle: const TextStyle(color: Colors.white)),
            onTap: ()=>ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Safety finding — requires clinician review; AI cannot close'))),
          ));
        }));
  }
}
