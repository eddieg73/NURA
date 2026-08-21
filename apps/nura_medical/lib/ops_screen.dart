import 'package:flutter/material.dart';

/// The NURA Ops tab — the practice front office (the Weave-equivalent):
/// the patient texts, the payments, the fax, the reviews.
class OpsScreen extends StatelessWidget {
  const OpsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('📋 NURA Ops — the back office')),
      body: ListView(
        padding: const EdgeInsets.all(12),
        children: const [
          _OpsTile(Icons.chat_outlined, 'Patient Texts',
              'The two-way SMS (the Twilio lane) — the office-number masking'),
          _OpsTile(Icons.payment_outlined, 'Payments',
              'The text-to-pay + the plans (the NMI lane)'),
          _OpsTile(Icons.fax_outlined, 'Fax',
              'The secure fax (the Documo lane — the key pending)'),
          _OpsTile(Icons.star_outline, 'Reviews',
              'The review invites + the responses (the Google lane)'),
          _OpsTile(Icons.event_available_outlined, 'Reminders',
              'The appointment reminders (the n8n workflows)'),
          _OpsTile(Icons.receipt_long_outlined, 'Akaunting Books',
              'The practice accounting (the Lab, the tailnet :8450)'),
        ],
      ),
    );
  }
}

class _OpsTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  const _OpsTile(this.icon, this.title, this.subtitle);

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      subtitle: Text(subtitle, style: const TextStyle(fontSize: 11)),
      onTap: () => ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('$title: the lane is wiring — check the status dashboard'), duration: const Duration(seconds: 2)),
      ),
    );
  }
}
