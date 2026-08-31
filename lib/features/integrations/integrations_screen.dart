import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:brawlerz_box/core/api/api_client.dart';
import 'package:brawlerz_box/shared/repositories/integration_repository.dart';
import 'package:brawlerz_box/shared/widgets/async_content.dart';
import 'package:brawlerz_box/shared/widgets/brawlerz_card.dart';

class IntegrationsScreen extends ConsumerStatefulWidget {
  const IntegrationsScreen({super.key});

  @override
  ConsumerState<IntegrationsScreen> createState() => _IntegrationsScreenState();
}

class _IntegrationsScreenState extends ConsumerState<IntegrationsScreen> {
  final Set<String> _busy = {};

  Future<void> _toggle(IntegrationConnectionModel item) async {
    if (_busy.contains(item.provider)) return;
    setState(() => _busy.add(item.provider));
    try {
      await ref.read(integrationRepositoryProvider).setConnected(
            item.provider,
            !item.connected,
          );
      ref.invalidate(integrationsProvider);
    } on ApiException catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(error.message), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _busy.remove(item.provider));
    }
  }

  @override
  Widget build(BuildContext context) {
    final integrations = ref.watch(integrationsProvider);
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'INTEGRATIONS',
          style: GoogleFonts.oswald(fontWeight: FontWeight.bold),
        ),
      ),
      body: integrations.when(
        loading: () => const AsyncLoadingView(),
        error: (error, _) => AsyncErrorView(
          error: error,
          onRetry: () => ref.invalidate(integrationsProvider),
        ),
        data: (items) => RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(integrationsProvider);
            await ref.read(integrationsProvider.future);
          },
          child: ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(20),
            children: [
              const BrawlerzCard(
                color: Color(0x1AFFB000),
                child: Text(
                  'These controls store connection state only. Apple Health, Garmin, WHOOP and Google Fit OAuth/token exchange still require provider-specific server verification before production use.',
                  style: TextStyle(fontSize: 12),
                ),
              ),
              const SizedBox(height: 24),
              Text(
                'HEALTH & WEARABLES',
                style: GoogleFonts.oswald(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                  color: const Color(0xFFFF4500),
                ),
              ),
              const SizedBox(height: 16),
              ...items.map(_buildTile),
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTile(IntegrationConnectionModel item) {
    final metadata = _metadata(item.provider);
    final busy = _busy.contains(item.provider);
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: BrawlerzCard(
        onTap: busy ? null : () => _toggle(item),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: metadata.color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(metadata.icon, color: metadata.color, size: 24),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    metadata.name,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    item.connected ? 'Enabled in profile' : 'Not enabled',
                    style: TextStyle(
                      color: item.connected ? Colors.green : Colors.grey,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
            if (busy)
              const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            else
              Icon(
                item.connected ? Icons.check_circle : Icons.add_circle_outline,
                color: item.connected ? Colors.green : Colors.grey,
                size: 20,
              ),
          ],
        ),
      ),
    );
  }

  ({String name, IconData icon, Color color}) _metadata(String provider) {
    switch (provider) {
      case 'apple_health':
        return (name: 'Apple Health', icon: Icons.favorite, color: Colors.red);
      case 'garmin':
        return (name: 'Garmin', icon: Icons.watch, color: Colors.blue);
      case 'whoop':
        return (name: 'WHOOP', icon: Icons.bolt, color: Colors.white);
      case 'google_fit':
        return (name: 'Google Fit', icon: Icons.directions_run, color: Colors.green);
      default:
        return (name: provider, icon: Icons.extension, color: Colors.grey);
    }
  }
}
