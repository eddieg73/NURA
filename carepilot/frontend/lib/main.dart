import 'package:flutter/material.dart';
import 'screens/home.dart';
import 'screens/work_queue.dart';
import 'screens/patient.dart';
import 'screens/risk.dart';
import 'screens/med_safety.dart';
import 'screens/quality.dart';
import 'screens/finance.dart';

void main() => runApp(const CarePilotApp());

class CarePilotApp extends StatelessWidget {
  const CarePilotApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CarePilot',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF0E7490)),
        useMaterial3: true,
      ),
      home: const RootShell(),
    );
  }
}

/// Bottom-nav shell — the 7 provider-facing surfaces.
class RootShell extends StatefulWidget {
  const RootShell({super.key});
  @override
  State<RootShell> createState() => _RootShellState();
}

class _RootShellState extends State<RootShell> {
  int _index = 0;
  static final _pages = [
    const HomeScreen(),        // CPHO Command Center
    const WorkQueueScreen(),   // Unified Work Queue
    const PatientSearchScreen(),// Patient
    const RiskScreen(),        // Risk / RAF
    const MedSafetyScreen(),   // Medication Safety
    const QualityScreen(),     // HEDIS/Stars
    const FinanceScreen(),     // Medical Economics
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _index, children: _pages),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.dashboard), label: 'Command'),
          NavigationDestination(icon: Icon(Icons.checklist), label: 'Queue'),
          NavigationDestination(icon: Icon(Icons.person_search), label: 'Patients'),
          NavigationDestination(icon: Icon(Icons.show_chart), label: 'Risk'),
          NavigationDestination(icon: Icon(Icons.medication), label: 'MedSafety'),
          NavigationDestination(icon: Icon(Icons.verified), label: 'Quality'),
          NavigationDestination(icon: Icon(Icons.account_balance), label: 'Finance'),
        ],
      ),
    );
  }
}
