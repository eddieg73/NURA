import 'package:flutter/material.dart';
import 'scribe_screen.dart';
import 'e6b_screen.dart';
import 'clinical_screen.dart';
import 'ops_screen.dart';
import 'account_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NURA Medical',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF0B3D91)),
        useMaterial3: true,
      ),
      home: const NuraHome(),
    );
  }
}

class NuraHome extends StatefulWidget {
  const NuraHome({super.key});

  @override
  State<NuraHome> createState() => _NuraHomeState();
}

class _NuraHomeState extends State<NuraHome> {
  int _tab = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('NURA — the ONE app')),
      body: IndexedStack(
        index: _tab,
        children: const [
          ScribeScreen(),     // 0 — the ambient scribe
          ClinicalScreen(),   // 1 — the dx/synthesis/scribe engines
          OpsScreen(),        // 2 — the inbox/texts/payments/fax/books
          E6BScreen(),        // 3 — the aviation E6B
          AccountScreen(),    // 4 — the license gate
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        onDestinationSelected: (i) => setState(() => _tab = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.mic), label: 'Scribe'),
          NavigationDestination(icon: Icon(Icons.monitor_heart_outlined), label: 'Clinical'),
          NavigationDestination(icon: Icon(Icons.forum_outlined), label: 'Ops'),
          NavigationDestination(icon: Icon(Icons.flight_takeoff), label: 'E6B'),
          NavigationDestination(icon: Icon(Icons.person_outline), label: 'Account'),
        ],
      ),
    );
  }
}
