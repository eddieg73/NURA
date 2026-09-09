import 'package:flutter/material.dart';
import '../api.dart';

/// Risk / RAF — V28-aligned scores with provenance; cross-model compare blocked by UI+server.
class RiskScreen extends StatefulWidget {
  const RiskScreen({super.key});
  @override State<RiskScreen> createState() => _RiskScreenState();
}
class _RiskScreenState extends State<RiskScreen> {
  List<dynamic> _scores=[]; String _err='';
  @override void initState(){super.initState(); _load();}
  Future<void> _load() async {
    try { final d=await Api.get('/api/risk-scores'); setState((){_scores=(d['scores'] as List?)??[]; _err='';}); }
    catch(e){ setState(()=>_err=e.toString()); }
  }
  @override Widget build(BuildContext context){
    return Scaffold(appBar: AppBar(title: const Text('Risk / RAF (V28)')),
      body: _err!='' ? Center(child: Text('Backend: $_err'))
        : ListView.builder(padding: const EdgeInsets.all(8), itemCount:_scores.length, itemBuilder:(_,i){
          final s=_scores[i];
          return Card(child: ListTile(
            leading: const Icon(Icons.show_chart, color: Colors.indigo),
            title: Text('${s['model']} v${s['version']} (${s['year']})'),
            subtitle: Text('clinical ${s['clinical']} · RAF ${s['raf']} · source ${s['source']} · ${s['components']}'),
            trailing: Chip(label: Text('${s['raf']}')),
            onTap: ()=>ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Cross-model comparison blocked — V28 only'))),
          ));
        }));
  }
}
