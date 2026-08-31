import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'account_screen.dart';
import 'clinical_screen.dart';
import 'core/models/models.dart';
import 'core/providers.dart';
import 'e6b_screen.dart';
import 'ops_screen.dart';
import 'screens/login_screen.dart';
import 'screens/review_queue_screen.dart';
import 'scribe_screen.dart';

class NuraMedicalApp extends ConsumerWidget {
  const NuraMedicalApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authControllerProvider);
    return MaterialApp(
      title: 'NURA Medical',
      debugShowCheckedModeBanner: false,
      theme: _theme(),
      home: auth.loading
          ? const _BootScreen()
          : auth.user == null
              ? const LoginScreen()
              : NuraHome(user: auth.user!),
    );
  }

  ThemeData _theme() {
    const seed = Color(0xFF087F8C);
    final scheme = ColorScheme.fromSeed(
      seedColor: seed,
      brightness: Brightness.light,
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: const Color(0xFFF5F8FA),
      appBarTheme: const AppBarTheme(
        centerTitle: false,
        backgroundColor: Colors.white,
        foregroundColor: Color(0xFF102A43),
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: Colors.white,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(18),
          side: const BorderSide(color: Color(0xFFD9E2EC)),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Color(0xFFBCCCDC)),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          minimumSize: const Size.fromHeight(50),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
      ),
    );
  }
}

class _BootScreen extends StatelessWidget {
  const _BootScreen();

  @override
  Widget build(BuildContext context) => const Scaffold(
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.monitor_heart_outlined, size: 52),
              SizedBox(height: 18),
              CircularProgressIndicator(),
              SizedBox(height: 12),
              Text('Restoring secure NURA session…'),
            ],
          ),
        ),
      );
}

class NuraHome extends StatefulWidget {
  const NuraHome({super.key, required this.user});

  final AppUser user;

  @override
  State<NuraHome> createState() => _NuraHomeState();
}

class _NuraHomeState extends State<NuraHome> {
  int _tab = 0;

  @override
  Widget build(BuildContext context) {
    final canReview =
        widget.user.role == 'reviewer' || widget.user.role == 'admin';
    final screens = <Widget>[
      const ScribeScreen(),
      const ClinicalScreen(),
      const OpsScreen(),
      if (canReview) const ReviewQueueScreen(),
      const E6BScreen(),
      AccountScreen(user: widget.user),
    ];
    final destinations = <NavigationDestination>[
      const NavigationDestination(icon: Icon(Icons.mic_none), label: 'Scribe'),
      const NavigationDestination(
        icon: Icon(Icons.monitor_heart_outlined),
        label: 'Clinical',
      ),
      const NavigationDestination(icon: Icon(Icons.task_alt), label: 'Ops'),
      if (canReview)
        const NavigationDestination(
          icon: Icon(Icons.verified_user_outlined),
          label: 'Review',
        ),
      const NavigationDestination(icon: Icon(Icons.flight_takeoff), label: 'E6B'),
      const NavigationDestination(icon: Icon(Icons.person_outline), label: 'Account'),
    ];
    final selected = _tab.clamp(0, screens.length - 1);
    return Scaffold(
      body: IndexedStack(index: selected, children: screens),
      bottomNavigationBar: NavigationBar(
        selectedIndex: selected,
        onDestinationSelected: (index) => setState(() => _tab = index),
        destinations: destinations,
      ),
    );
  }
}
