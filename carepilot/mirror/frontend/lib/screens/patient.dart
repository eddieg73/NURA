import 'package:flutter/material.dart';
import '../api.dart';

/// Patient search + summary (conditions, risk, gaps, programs, alerts).
class PatientSearchScreen extends StatefulWidget {
  const PatientSearchScreen({super.key});
  @override State<PatientSearchScreen> createState() => _PatientSearchScreenState();
}
class _PatientSearchScreenState extends State<PatientSearchScreen> {
  final _q = TextEditingController(); List<dynamic> _results=[]; Map<String,dynamic>? _detail; String _err='';
  Future<void> _search() async {
    try { final d=await Api.get('/api/patients/search?q=${Uri.encodeComponent(_q.text)}'); setState((){_results=(d['results'] as List?)??[]; _err='';}); }
    catch(e){ setState(()=>_err=e.toString()); }
  }
  Future<void> _open(String pid) async {
    try { final d=await Api.get('/api/patients/$pid/summary'); setState(()=>_detail=d); }
    catch(e){ setState(()=>_err=e.toString()); }
  }
  @override Widget build(BuildContext context) {
    if (_detail!=null) return _detailView();
    return Scaffold(appBar: AppBar(title: const Text('Patients')),
      body: Column(children:[
        Padding(padding: const EdgeInsets.all(8), child: Row(children:[
          Expanded(child: TextField(controller:_q, decoration: const InputDecoration(hintText:'Name / condition / payer', border: OutlineInputBorder()), onSubmitted:(_)=>_search())),
          IconButton(onPressed:_search, icon: const Icon(Icons.search))])),
        _err!='' ? Expanded(child: Center(child: Text('Backend: $_err')))
          : Expanded(child: ListView.builder(itemCount:_results.length, itemBuilder:(_,i){ final p=_results[i]; return ListTile(
            leading: const CircleAvatar(child: Icon(Icons.person)), title: Text(p['name'] ?? ''),
            subtitle: Text('${p['payer']} · ${(p['conditions'] as List?)?.join(', ')}'),
            trailing: const Icon(Icons.chevron_right), onTap: ()=>_open(p['id'])); })),
      ]));
  }
  Widget _detailView(){
    final p=_detail!['patient'] as Map<String,dynamic>; final gaps=(_detail!['gaps'] as List?) ?? [];
    return Scaffold(appBar: AppBar(title: Text(p['name'] ?? ''), actions:[IconButton(icon: const Icon(Icons.arrow_back), onPressed: ()=>setState(()=>_detail=null))]),
      body: ListView(padding: const EdgeInsets.all(12), children:[
        Text('${p['mrn']} · ${p['payer']} · ${p['product'] ?? '—'}'),
        const Divider(),
        Text('Conditions: ${(p['conditions'] as List?)?.join(', ') ?? '—'}'),
        Text('Programs: ${(p['programs'] as List?)?.join(', ') ?? '—'}'),
        const SizedBox(height:8),
        Text('Risk (V28): ${_detail!['risks'] ?? '—'}'),
        const Divider(),
        Text('Open care gaps (${gaps.length})'),
        ...gaps.map((g)=>ListTile(leading: const Icon(Icons.flag, color: Colors.amber), title: Text(g['measure'] ?? ''), subtitle: Text('${g['status']} · evidence ${g['evidence']}'))),
        Text('Med safety alerts: ${(_detail!['alerts'] as List?)?.length ?? 0}'),
      ]));
  }
}
