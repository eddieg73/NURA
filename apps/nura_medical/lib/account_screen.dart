import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/config/app_config.dart';
import 'core/models/models.dart';
import 'core/providers.dart';

class AccountScreen extends ConsumerStatefulWidget {
  const AccountScreen({super.key, required this.user});

  final AppUser user;

  @override
  ConsumerState<AccountScreen> createState() => _AccountScreenState();
}

class _AccountScreenState extends ConsumerState<AccountScreen> {
  bool _busy = false;
  String? _error;
  LegalConfig? _legal;

  @override
  void initState() {
    super.initState();
    _loadLegal();
  }

  Future<void> _loadLegal() async {
    try {
      final legal = await ref.read(legalRepositoryProvider).load();
      if (mounted) setState(() => _legal = legal);
    } catch (_) {
      // The compile-time URLs remain visible if the public legal endpoint is
      // temporarily unavailable.
    }
  }

  Future<void> _export() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final data = await ref.read(authRepositoryProvider).exportAccount();
      if (!mounted) return;
      await showDialog<void>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Account data export'),
          content: SizedBox(
            width: 640,
            child: SingleChildScrollView(
              child: SelectableText(
                const JsonEncoder.withIndent('  ').convert(data),
                style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
              ),
            ),
          ),
          actions: [
            FilledButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Done'),
            ),
          ],
        ),
      );
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _deleteAccount() async {
    final password = TextEditingController();
    bool obscure = true;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Permanently delete account?'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'This deletes your account, sessions, encounters, drafts, and operations tasks. This action cannot be undone.',
              ),
              const SizedBox(height: 14),
              TextField(
                controller: password,
                obscureText: obscure,
                decoration: InputDecoration(
                  labelText: 'Confirm password',
                  suffixIcon: IconButton(
                    onPressed: () => setDialogState(() => obscure = !obscure),
                    icon: Icon(obscure ? Icons.visibility : Icons.visibility_off),
                  ),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogContext, false),
              child: const Text('Cancel'),
            ),
            FilledButton(
              style: FilledButton.styleFrom(backgroundColor: Colors.red),
              onPressed: () => Navigator.pop(dialogContext, true),
              child: const Text('Delete permanently'),
            ),
          ],
        ),
      ),
    );
    if (confirmed != true || password.text.isEmpty) {
      password.dispose();
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    final success = await ref
        .read(authControllerProvider.notifier)
        .deleteAccount(password.text);
    password.dispose();
    if (mounted && !success) {
      setState(() {
        _busy = false;
        _error = ref.read(authControllerProvider).error;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final privacy = _legal?.privacyPolicyUrl ?? AppConfig.privacyPolicyUrl;
    final terms = _legal?.termsUrl ?? AppConfig.termsUrl;
    final support = _legal?.supportUrl ?? AppConfig.supportUrl;
    return Scaffold(
      appBar: AppBar(title: const Text('Account & Safety')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 30,
                    child: Text(
                      widget.user.fullName
                          .split(RegExp(r'\s+'))
                          .where((part) => part.isNotEmpty)
                          .take(2)
                          .map((part) => part[0].toUpperCase())
                          .join(),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          widget.user.fullName,
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        Text(widget.user.email),
                        const SizedBox(height: 4),
                        Chip(label: Text(widget.user.role.toUpperCase())),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 14),
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.cloud_outlined),
                  title: const Text('Service environment'),
                  subtitle: Text(
                    '${AppConfig.appEnvironment}\n${AppConfig.apiBaseUrl}',
                  ),
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.download_outlined),
                  title: const Text('Export my account data'),
                  subtitle: const Text('Review a JSON export of your NURA records.'),
                  enabled: !_busy,
                  onTap: _export,
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.privacy_tip_outlined),
                  title: const Text('Privacy policy'),
                  subtitle: SelectableText(privacy),
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.description_outlined),
                  title: const Text('Terms of use'),
                  subtitle: SelectableText(terms),
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.support_agent),
                  title: const Text('Support'),
                  subtitle: SelectableText(support),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Clinical safety notice',
                    style: TextStyle(fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _legal?.clinicalDisclaimer ??
                        'NURA generates clinician decision-support drafts. It does not replace professional judgment, establish a diagnosis, or authorize treatment. Provider review is required.',
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Do not use NURA for emergency communication or as the sole source of a time-critical clinical decision.',
                    style: TextStyle(fontWeight: FontWeight.w700),
                  ),
                ],
              ),
            ),
          ),
          if (_error != null) ...[
            const SizedBox(height: 14),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.errorContainer,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(_error!),
            ),
          ],
          const SizedBox(height: 14),
          OutlinedButton.icon(
            onPressed: _busy
                ? null
                : () => ref.read(authControllerProvider.notifier).logout(),
            icon: const Icon(Icons.logout),
            label: const Text('Sign out'),
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            style: OutlinedButton.styleFrom(foregroundColor: Colors.red),
            onPressed: _busy ? null : _deleteAccount,
            icon: const Icon(Icons.delete_forever_outlined),
            label: const Text('Delete account permanently'),
          ),
          const SizedBox(height: 100),
        ],
      ),
    );
  }
}
