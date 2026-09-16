import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'state/app_state.dart';
import 'screens/home.dart';
import 'screens/work_queue.dart';
import 'screens/patient.dart';
import 'screens/risk.dart';
import 'screens/med_safety.dart';
import 'screens/quality.dart';
import 'screens/finance.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AppState()),
      ],
      child: const CarePilotApp(),
    ),
  );
}

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

/// Bottom-nav shell — Provider-driven IndexedStack over the 7 surfaces.
class RootShell extends StatelessWidget {
  const RootShell({super.key});

  static const _pages = <Widget>[
    HomeScreen(),
    WorkQueueScreen(),
    PatientSearchScreen(),
    RiskScreen(),
    MedSafetyScreen(),
    QualityScreen(),
    FinanceScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final app = context.watch<AppState>();

    return Scaffold(
      body: IndexedStack(index: app.selectedIndex, children: _pages),
      bottomNavigationBar: NavigationBar(
        selectedIndex: app.selectedIndex,
        onDestinationSelected: context.read<AppState>().selectTab,
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
