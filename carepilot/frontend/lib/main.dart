import 'package:flutter/material.dart';
import 'home.dart';

void main() {
  runApp(const CarePilotApp());
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
      home: const HomeScreen(),
    );
  }
}

/// Backend base for the Python FastAPI service (overridable via --dart-define).
const String kApiBase = String.fromEnvironment('CAREPILOT_API', defaultValue: 'http://localhost:8000');
