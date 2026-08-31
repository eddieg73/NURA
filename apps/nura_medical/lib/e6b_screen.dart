import 'dart:math' as math;

import 'package:flutter/material.dart';

class E6BScreen extends StatefulWidget {
  const E6BScreen({super.key});

  @override
  State<E6BScreen> createState() => _E6BScreenState();
}

class _E6BScreenState extends State<E6BScreen> {
  final _speed = TextEditingController(text: '120');
  final _minutes = TextEditingController(text: '60');
  final _distance = TextEditingController(text: '120');
  final _fuelBurn = TextEditingController(text: '10');
  final _windSpeed = TextEditingController(text: '15');
  final _windAngle = TextEditingController(text: '30');
  String _result = 'Enter values and select a calculation.';

  @override
  void dispose() {
    for (final controller in [
      _speed,
      _minutes,
      _distance,
      _fuelBurn,
      _windSpeed,
      _windAngle,
    ]) {
      controller.dispose();
    }
    super.dispose();
  }

  double? _value(TextEditingController controller) =>
      double.tryParse(controller.text.trim());

  void _distanceResult() {
    final speed = _value(_speed);
    final minutes = _value(_minutes);
    if (speed == null || minutes == null || speed < 0 || minutes < 0) {
      _invalid();
      return;
    }
    setState(() => _result =
        'Distance: ${(speed * minutes / 60).toStringAsFixed(1)} nautical miles');
  }

  void _timeResult() {
    final speed = _value(_speed);
    final distance = _value(_distance);
    if (speed == null || distance == null || speed <= 0 || distance < 0) {
      _invalid();
      return;
    }
    final totalMinutes = distance / speed * 60;
    final hours = totalMinutes ~/ 60;
    final minutes = (totalMinutes % 60).round();
    setState(() => _result = 'Time en route: ${hours}h ${minutes}m');
  }

  void _fuelResult() {
    final burn = _value(_fuelBurn);
    final minutes = _value(_minutes);
    if (burn == null || minutes == null || burn < 0 || minutes < 0) {
      _invalid();
      return;
    }
    setState(() => _result =
        'Estimated fuel: ${(burn * minutes / 60).toStringAsFixed(1)} gallons');
  }

  void _windResult() {
    final speed = _value(_windSpeed);
    final angle = _value(_windAngle);
    if (speed == null || angle == null || speed < 0) {
      _invalid();
      return;
    }
    final radians = angle * math.pi / 180;
    final crosswind = speed * math.sin(radians).abs();
    final headwind = speed * math.cos(radians);
    final component = headwind >= 0 ? 'headwind' : 'tailwind';
    setState(() => _result =
        'Crosswind: ${crosswind.toStringAsFixed(1)} kt · $component: ${headwind.abs().toStringAsFixed(1)} kt');
  }

  void _invalid() => setState(() => _result = 'Enter valid non-negative numbers.');

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('E6B Utility')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.amber.withValues(alpha: 0.16),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: Colors.amber.shade700),
            ),
            child: const Text(
              'Advisory calculation aid only. Verify all values using approved aircraft documentation, current weather, official planning tools, and pilot judgment.',
              style: TextStyle(fontWeight: FontWeight.w700),
            ),
          ),
          const SizedBox(height: 14),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  _numberField(_speed, 'Ground speed', 'kt'),
                  const SizedBox(height: 12),
                  _numberField(_minutes, 'Time', 'minutes'),
                  const SizedBox(height: 12),
                  _numberField(_distance, 'Distance', 'nautical miles'),
                  const SizedBox(height: 12),
                  _numberField(_fuelBurn, 'Fuel burn', 'gallons/hour'),
                  const SizedBox(height: 12),
                  _numberField(_windSpeed, 'Wind speed', 'kt'),
                  const SizedBox(height: 12),
                  _numberField(_windAngle, 'Wind angle', 'degrees off runway/track'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 14),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              FilledButton.tonal(
                onPressed: _distanceResult,
                child: const Text('Distance'),
              ),
              FilledButton.tonal(
                onPressed: _timeResult,
                child: const Text('Time'),
              ),
              FilledButton.tonal(
                onPressed: _fuelResult,
                child: const Text('Fuel'),
              ),
              FilledButton.tonal(
                onPressed: _windResult,
                child: const Text('Wind components'),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: SelectableText(
                _result,
                style: Theme.of(context)
                    .textTheme
                    .titleLarge
                    ?.copyWith(fontWeight: FontWeight.w800),
              ),
            ),
          ),
          const SizedBox(height: 80),
        ],
      ),
    );
  }

  Widget _numberField(
    TextEditingController controller,
    String label,
    String suffix,
  ) =>
      TextField(
        controller: controller,
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(labelText: label, suffixText: suffix),
      );
}
