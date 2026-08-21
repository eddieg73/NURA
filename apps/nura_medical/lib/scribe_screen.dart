import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';

/// The NURA Scribe screen — the ambient documentation lane.
/// Dictation in → the structured SOAP note out (Med42) → the provider review label.
/// The API base = the NURA tools API (override per deployment).
const String kScribeApi = 'http://100.76.175.91:8095/scribe'; // the tailnet gateway (the fallback: 127.0.0.1 on-device)

class ScribeScreen extends StatefulWidget {
  const ScribeScreen({super.key});

  @override
  State<ScribeScreen> createState() => _ScribeScreenState();
}

class _ScribeScreenState extends State<ScribeScreen> {
  final TextEditingController _dictation = TextEditingController();
  String _note = '';
  bool _busy = false;
  String _error = '';

  Future<void> _scribe() async {
    if (_dictation.text.trim().isEmpty) return;
    setState(() { _busy = true; _error = ''; });
    try {
      final client = HttpClient();
      final req = await client.postUrl(Uri.parse(kScribeApi));
      req.headers.contentType = ContentType.json;
      req.write(jsonEncode({'text': _dictation.text.trim()}));
      final res = await req.close();
      final body = await res.transform(utf8.decoder).join();
      final note = jsonDecode(body)['note'] ?? '(empty response)';
      setState(() { _note = note; _busy = false; });
    } catch (e) {
      setState(() { _error = 'Scribe call failed: $e'; _busy = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('NURA Scribe')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text('Dictate the encounter — the structured note returns for YOUR review.',
                style: TextStyle(fontSize: 13, color: Colors.grey)),
            const SizedBox(height: 12),
            TextField(
              controller: _dictation,
              maxLines: 6,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'Example: 72 year old female, three days of fever and cough...',
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                ElevatedButton.icon(
                  onPressed: _busy ? null : _scribe,
                  icon: _busy
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.mic),
                  label: Text(_busy ? 'Scribing…' : 'Generate the note'),
                ),
              ],
            ),
            if (_error.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(_error, style: const TextStyle(color: Colors.red)),
            ],
            const SizedBox(height: 16),
            Expanded(
              child: SingleChildScrollView(
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(_note.isEmpty
                      ? 'The structured SOAP note appears here — flagged sections marked [review].'
                      : _note),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
