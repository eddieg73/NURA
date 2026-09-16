import 'package:flutter/material.dart';
import '../api.dart';

/// CPHO Command Center — one screen with the key population numbers (risk, admissions, quality, RAF, finance).
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override State<HomeScreen> createState() => _HomeScreenState();
}
class _HomeScreenState extends State<HomeScreen> {
  Map<String, dynamic>? _fin; Map<String, dynamic>? _util; Map<String, dynamic>? _risk;
  String? _err;
  @override void initState() { super.initState(); _load(); }
  Future<void> _load() async {
    try {
      final fin = await Api.get('/api/financial-summary');
      final util = await Api.get('/api/utilization');
      final risk = await Api.get('/api/risk-scores');
      setState(() { _fin = fin; _util = util; _risk = risk; _err = null; });
    } catch (e) { setState(() => _err = e.toString()); }
  }
  @override Widget build(BuildContext context) {
    final contracts = (_fin?['contracts'] as List?) ?? [];
    double totalPaid = contracts.fold(0, (s, c) => s + (c['paid'] as num? ?? 0).toDouble());
    return Scaffold(
      appBar: AppBar(title: const Text('CPHO Command Center'), actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _load)]),
      body: _err != null
        ? Center(child: Text('Backend: $_err'))
        : ListView(padding: const EdgeInsets.all(12), children: [
            GridView.count(crossAxisCount: 2, shrinkWrap: true, physics: const NeverScrollableScrollPhysics(),
              childAspectRatio: 1.5, children: [
                _tile('Total Paid', '${totalPaid.toStringAsFixed(0)}', Icons.attach_money, Colors.teal),
                _tile('Admissions', '${(_util?['admissions'] ?? 0)}', Icons.local_hospital, Colors.red),
                _tile('Risk Scores', '${(_risk?['scores'] as List?)?.length ?? 0}', Icons.show_chart, Colors.indigo),
                _tile('Contracts', '${contracts.length}', Icons.account_balance, Colors.orange),
              ]),
            const SizedBox(height: 12),
            _section('Population alerts (drill to patients)'),
            _row('Open care gaps', '${_gapCount(contracts)}', Icons.flag, Colors.amber),
            _row('Med safety flags', 'open', Icons.medication, Colors.red),
            _row('High-cost patients', '${(_util?['top_high_cost'] as List?)?.length ?? 0}', Icons.person, Colors.indigo),
          ]),
    );
  }
  int _gapCount(List c) => 0;
  Widget _tile(String label, String value, IconData icon, Color color) => Card(
    child: Padding(padding: const EdgeInsets.all(8), child: Column(mainAxisAlignment: MainAxisAlignment.center,
      children: [Icon(icon, color: color), Text(value, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)), Text(label, textAlign: TextAlign.center)])));
  Widget _section(String t) => Padding(padding: const EdgeInsets.only(bottom: 4), child: Text(t, style: const TextStyle(fontWeight: FontWeight.bold)));
  Widget _row(String label, String value, IconData icon, Color c) => ListTile(
    leading: Icon(icon, color: c), title: Text(label), trailing: Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
    onTap: () => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Drill: $label'))));
}
