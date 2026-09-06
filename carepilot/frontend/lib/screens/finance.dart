import 'package:flutter/material.dart';
import '../api.dart';

/// Finance — medical economics / contract performance (paid, incurred, estimated, PMPM).
class FinanceScreen extends StatefulWidget {
  const FinanceScreen({super.key});
  @override State<FinanceScreen> createState() => _FinanceScreenState();
}
class _FinanceScreenState extends State<FinanceScreen> {
  List<dynamic> _contracts=[]; String _err='';
  @override void initState(){super.initState(); _load();}
  Future<void> _load() async {
    try { final d=await Api.get('/api/financial-summary'); setState((){_contracts=(d['contracts'] as List?)??[]; _err='';}); }
    catch(e){ setState(()=>_err=e.toString()); }
  }
  @override Widget build(BuildContext context){
    return Scaffold(appBar: AppBar(title: const Text('Medical Economics')),
      body: _err!='' ? Center(child: Text('Backend: $_err'))
        : ListView.builder(padding: const EdgeInsets.all(8), itemCount:_contracts.length, itemBuilder:(_,i){
          final c=_contracts[i];
          return Card(child: ListTile(
            leading: const Icon(Icons.account_balance, color: Colors.orange),
            title: Text(c['contract'] ?? ''),
            subtitle: Text('paid ${c['paid']} · incurred ${c['incurred']} · est ${c['est']}'),
            trailing: Column(mainAxisAlignment: MainAxisAlignment.center, children:[
              Text('PMPM ${c['pmpm']}', style: const TextStyle(fontWeight: FontWeight.bold)),
              Text((c['incurred'] as num? ?? 0) > (c['paid'] as num? ?? 0) ? '▲variance' : '✓', style: TextStyle(color: (c['incurred'] as num? ?? 0) > (c['paid'] as num? ?? 0) ? Colors.red : Colors.green)),
            ]),
            onTap: ()=>ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Drill ${c['contract']} → member → claim'))),
          ));
        }));
  }
}
