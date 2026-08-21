import 'dart:math' as math;
import 'package:flutter/material.dart';

/// The NURA E6B — the aviation flight computer (the pilot's lane).
/// The time/fuel/distance triangle + the wind correction + the TAS.
class E6BScreen extends StatefulWidget {
  const E6BScreen({super.key});
  @override
  State<E6BScreen> createState() => _E6BScreenState();
}

class _E6BScreenState extends State<E6BScreen> {
  final _tas = TextEditingController(text: '150');
  final _windDir = TextEditingController(text: '0');
  final _windSpd = TextEditingController(text: '15');
  final _course = TextEditingController(text: '090');
  final _dist = TextEditingController(text: '300');
  String _gsResult = '';
  String _eteResult = '';
  String _fuelResult = '';
  final _burn = TextEditingController(text: '14');

  void _calc() {
    final tas = double.tryParse(_tas.text) ?? 0;
    final wd = double.tryParse(_windDir.text) ?? 0;
    final ws = double.tryParse(_windSpd.text) ?? 0;
    final crs = double.tryParse(_course.text) ?? 0;
    final dist = double.tryParse(_dist.text) ?? 0;
    final burn = double.tryParse(_burn.text) ?? 0;
    // the wind triangle (the simplified — the full E6B math)
    final windAngle = ((wd - crs) % 360 + 360) % 360; // the relative wind
    final rad = windAngle * math.pi / 180;
    final crosswind = ws * math.sin(rad);
    final headwind = ws * math.cos(rad);
    final wcaDeg = (tas <= 0) ? 0.0 : (crosswind / tas) * 60 / math.pi; // the degrees correction (the tas guard)
    final hdg = (crs + wcaDeg) % 360;
    final gs = (tas <= 0) ? 0.0 : tas - headwind;
    final eteH = dist / (gs == 0 ? 1 : gs);
    setState(() {
      _gsResult = 'GS ${gs.toStringAsFixed(0)} kt · HDG ${hdg.toStringAsFixed(0)}°';
      _eteResult = 'ETE ${(eteH * 60).toStringAsFixed(0)} min (${eteH.toStringAsFixed(2)} h)';
      _fuelResult = burn > 0 ? 'Fuel ${(burn * eteH).toStringAsFixed(1)} gal + reserve' : '';
    });
  }

  Widget _field(TextEditingController c, String label) {
    return TextField(
      controller: c,
      keyboardType: TextInputType.number,
      decoration: InputDecoration(labelText: label, isDense: true),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('✈️ NURA E6B — the flight computer')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _field(_tas, 'True Airspeed (kt)'),
            _field(_windDir, 'Wind Direction (°)'),
            _field(_windSpd, 'Wind Speed (kt)'),
            _field(_course, 'Course (°)'),
            _field(_dist, 'Distance (nm)'),
            _field(_burn, 'Fuel Burn (gal/h)'),
            const SizedBox(height: 12),
            FilledButton(onPressed: _calc, child: const Text('CALCULATE')),
            const SizedBox(height: 16),
            Text(_gsResult, style: Theme.of(context).textTheme.titleMedium),
            Text(_eteResult, style: Theme.of(context).textTheme.titleMedium),
            Text(_fuelResult, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 24),
            const Text('PROVIDER/PILOT USE — the planning aid, not the primary navigation.',
                style: TextStyle(fontSize: 11)),
          ],
        ),
      ),
    );
  }
}
