import 'package:flutter/material.dart';
import '../api.dart';

/// Quality — HEDIS/Stars measure numerator/denominator with proof.
class QualityScreen extends StatefulWidget {
  const QualityScreen({super.key});
  @override State<QualityScreen> createState() => _QualityScreenState();
}
class _QualityScreenState extends State<QualityScreen> {
  Map<String,dynamic>? _m; String _err='';
  @override void initState(){super.initState(); _load();}
  Future<void> _load() async {
    try { final d=await Api.get('/api/measure/HEDIS%20HbA1c'); setState((){_m=d; _err='';}); }
    catch(e){ setState(()=>_err=e.toString()); }
  }
  @override Widget build(BuildContext context){
    final m=_m;
    return Scaffold(appBar: AppBar(title: const Text('HEDIS / Stars')),
      body: _err!='' ? Center(child: Text('Backend: $_err'))
        : m==null ? const Center(child: CircularProgressIndicator())
        : ListView(padding: const EdgeInsets.all(12), children:[
            Text(m['measure'] ?? 'HEDIS measure', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height:8),
            Row(children:[
              Expanded(child: _num('Numerator', m['numerator'] ?? 0, Colors.green)),
              Expanded(child: _num('Denominator', m['denominator'] ?? 0, Colors.orange)),
            ]),
            const Divider(height:24),
            Text('Evidence (per gap)'),
            ...((m['evidence'] as List?) ?? []).map((e)=>ListTile(dense:true, leading: const Icon(Icons.verified, color: Colors.green), title: Text('$e'))),
            const SizedBox(height:8),
            Text('Open gaps: ${(m['open_gaps'] as List?)?.length ?? 0} — open the patient list'),
          ]));
  }
  Widget _num(String label, int val, Color c) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Text('$val', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: c)),
            Text(label),
          ],
        ),
      ),
    );
  }
}
