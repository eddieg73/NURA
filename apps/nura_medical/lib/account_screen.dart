import 'package:flutter/material.dart';

/// The NURA Account tab — the license gate (the NPI or the paramedic
/// license — the founder's law) + the app settings.
class AccountScreen extends StatelessWidget {
  const AccountScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('🔐 NURA Account')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: ListTile(
              leading: const Icon(Icons.verified_user_outlined),
              title: const Text('The license gate'),
              subtitle: const Text('The NPI or the paramedic license required — '
                  'the clinical features unlock on the verified credential.'),
              onTap: () => ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('The license gate: the NPI/paramedic verification wires with the Codemagic release'), duration: Duration(seconds: 2)),
              ),
            ),
          ),
          Card(
            child: ListTile(
              leading: const Icon(Icons.person_outline),
              title: const Text('The provider profile'),
              subtitle: const Text('The name, the credentials, the NPI — the '
                  'attestation for the signed documentation.'),
              onTap: () => ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('The profile lane is wiring — the NPI attestation ships with the provider verification'), duration: Duration(seconds: 2)),
              ),
            ),
          ),
          Card(
            child: ListTile(
              leading: const Icon(Icons.settings_outlined),
              title: const Text('The settings'),
              subtitle: const Text('The local-first routing · the draft-label '
                  'toggles · the audit-log review.'),
              onTap: () => ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('The settings lane is wiring — the routing doctrine lives in the vault'), duration: Duration(seconds: 2)),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text('The ONE app · the NURA OS · the provider-gated, the '
              'audit-friendly, the local-first.',
              style: TextStyle(fontSize: 11, color: Colors.grey.shade600)),
        ],
      ),
    );
  }
}
