import 'package:flutter/material.dart';
import 'dart:convert';
import 'dart:io';

/// The NURA Clinical tab — the dx engine, the lab trends, the synthesis.
/// Each output = the DRAFT-labeled (the provider review).
class ClinicalScreen extends StatefulWidget {
  const ClinicalScreen({super.key});
  @override
  State<ClinicalScreen> createState() => _ClinicalScreenState();
}

class _ClinicalScreenState extends State<ClinicalScreen> {
  final _caseText = TextEditingController();
  String _output = 'The clinical engines await — enter the case.';
  bool _busy = false;

  Future<void> _run(String tool) async {
    setState(() { _busy = true; _output = 'Running the $tool engine...'; });
    try {
      final client = HttpClient();
      final req = await client.postUrl(Uri.parse('http://127.0.0.1:8095/$tool'));
      req.headers.contentType = ContentType.json;
      req.write(jsonEncode({'text': _caseText.text}));
      final res = await req.close();
      final body = await res.transform(utf8.decoder).join();
      setState(() { _output = '$body\n\n[DRAFT — PROVIDER APPROVAL REQUIRED]'; });
      client.close();
    } catch (e) {
      setState(() { _output = 'The engine lane: ${e.toString().substring(0, 80)}'; });
    } finally {
      setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('🩺 NURA Clinical')),
      body: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(children: [
          TextField(controller: _caseText, maxLines: 3,
            decoration: const InputDecoration(
              labelText: 'The case (the history, the exam, the labs)',
              border: OutlineInputBorder())),
          const SizedBox(height: 8),
          Row(children: [
            Expanded(child: FilledButton(onPressed: _busy ? null : () => _run('dx'),
              child: const Text('DX'))),
            Expanded(child: FilledButton(onPressed: _busy ? null : () => _run('synthesis'),
              child: const Text('SYNTHESIS'))),
            Expanded(child: FilledButton(onPressed: _busy ? null : () => _run('scribe'),
              child: const Text('SCRIBE'))),
          ]),
          const SizedBox(height: 12),
          Expanded(child: SingleChildScrollView(
            child: Text(_output, style: const TextStyle(fontSize: 13)))),
        ]),
      ),
    );
  }
}
