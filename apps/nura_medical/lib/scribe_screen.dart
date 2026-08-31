import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:speech_to_text/speech_recognition_result.dart';
import 'package:speech_to_text/speech_to_text.dart';

import 'core/models/models.dart';
import 'core/providers.dart';
import 'widgets/clinical_draft_view.dart';

class ScribeScreen extends ConsumerStatefulWidget {
  const ScribeScreen({super.key});

  @override
  ConsumerState<ScribeScreen> createState() => _ScribeScreenState();
}

class _ScribeScreenState extends ConsumerState<ScribeScreen> {
  final _note = TextEditingController();
  final _patientReference = TextEditingController();
  final _speech = SpeechToText();
  bool _speechAvailable = false;
  bool _listening = false;
  bool _consent = false;
  bool _submitting = false;
  String? _error;
  ClinicalDraft? _draft;

  @override
  void initState() {
    super.initState();
    _initializeSpeech();
  }

  Future<void> _initializeSpeech() async {
    final available = await _speech.initialize(
      onStatus: (status) {
        if (!mounted) return;
        setState(() => _listening = status == 'listening');
      },
      onError: (error) {
        if (!mounted) return;
        setState(() {
          _listening = false;
          _error = 'Dictation stopped: ${error.errorMsg}';
        });
      },
    );
    if (mounted) setState(() => _speechAvailable = available);
  }

  void _onSpeechResult(SpeechRecognitionResult result) {
    setState(() {
      _note.text = result.recognizedWords;
      _note.selection = TextSelection.collapsed(offset: _note.text.length);
    });
  }

  Future<void> _toggleListening() async {
    setState(() => _error = null);
    if (_speech.isListening) {
      await _speech.stop();
      if (mounted) setState(() => _listening = false);
      return;
    }
    if (!_speechAvailable) await _initializeSpeech();
    if (!_speechAvailable) {
      setState(() => _error =
          'Microphone or speech-recognition permission is unavailable. You can still type the note.');
      return;
    }
    await _speech.listen(
      onResult: _onSpeechResult,
      partialResults: true,
      cancelOnError: true,
    );
    if (mounted) setState(() => _listening = true);
  }

  Future<void> _submit() async {
    final text = _note.text.trim();
    if (text.isEmpty) {
      setState(() => _error = 'Enter or dictate source text first.');
      return;
    }
    if (!_consent) {
      setState(() => _error =
          'Confirm patient consent and your authority to submit the clinical text.');
      return;
    }
    await _speech.stop();
    setState(() {
      _submitting = true;
      _error = null;
      _draft = null;
    });
    try {
      final draft = await ref.read(clinicalRepositoryProvider).createDraft(
            operation: 'scribe',
            caseText: text,
            consentAttested: _consent,
            patientReference: _patientReference.text,
          );
      if (mounted) setState(() => _draft = draft);
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  void dispose() {
    _speech.stop();
    _note.dispose();
    _patientReference.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('NURA Ambient Scribe'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: Chip(
              avatar: const Icon(Icons.lock_outline, size: 16),
              label: const Text('Secure draft'),
              backgroundColor: Colors.teal.withValues(alpha: 0.1),
            ),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Text(
                    'Capture source facts',
                    style: TextStyle(fontSize: 19, fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'Use the microphone only with patient knowledge and according to your organization’s consent policy. Speech recognition may be processed by the device platform.',
                  ),
                  const SizedBox(height: 14),
                  TextField(
                    controller: _patientReference,
                    decoration: const InputDecoration(
                      labelText: 'Patient reference (minimum necessary)',
                      hintText: 'Prefer a de-identified or internal reference',
                      prefixIcon: Icon(Icons.badge_outlined),
                    ),
                  ),
                  const SizedBox(height: 14),
                  TextField(
                    controller: _note,
                    minLines: 8,
                    maxLines: 18,
                    textCapitalization: TextCapitalization.sentences,
                    decoration: const InputDecoration(
                      labelText: 'History, examination, tests, and clinician observations',
                      alignLabelWithHint: true,
                    ),
                  ),
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    onPressed: _submitting ? null : _toggleListening,
                    icon: Icon(_listening ? Icons.stop_circle : Icons.mic),
                    label: Text(_listening ? 'Stop dictation' : 'Start dictation'),
                  ),
                  SwitchListTile.adaptive(
                    contentPadding: EdgeInsets.zero,
                    value: _consent,
                    onChanged: _submitting
                        ? null
                        : (value) => setState(() => _consent = value),
                    title: const Text('Consent and authority attested'),
                    subtitle: const Text(
                      'I am authorized to capture and process this clinical information.',
                    ),
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: 8),
                    _ErrorBanner(message: _error!),
                  ],
                  const SizedBox(height: 12),
                  FilledButton.icon(
                    onPressed: _submitting ? null : _submit,
                    icon: _submitting
                        ? const SizedBox.square(
                            dimension: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.auto_awesome),
                    label: Text(_submitting
                        ? 'Generating controlled draft…'
                        : 'Generate scribe draft'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 14),
          if (_draft != null) ClinicalDraftView(draft: _draft!),
          const SizedBox(height: 80),
        ],
      ),
    );
  }
}

class _ErrorBanner extends StatelessWidget {
  const _ErrorBanner({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) => Semantics(
        liveRegion: true,
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.errorContainer,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            message,
            style: TextStyle(
              color: Theme.of(context).colorScheme.onErrorContainer,
            ),
          ),
        ),
      );
}
