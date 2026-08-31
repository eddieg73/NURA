import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:brawlerz_box/core/theme.dart';
import 'package:brawlerz_box/app/router.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    const ProviderScope(
      child: BrawlerzBoxApp(),
    ),
  );
}

class BrawlerzBoxApp extends ConsumerWidget {
  const BrawlerzBoxApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'Brawlerz Box',
      debugShowCheckedModeBanner: false,
      theme: BrawlerzTheme.darkTheme,
      routerConfig: router,
    );
  }
}
