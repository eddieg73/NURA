import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:brawlerz_box/shared/widgets/brawlerz_card.dart';
import 'package:brawlerz_box/shared/widgets/action_button.dart';

class AiCoachScreen extends StatefulWidget {
  const AiCoachScreen({super.key});

  @override
  State<AiCoachScreen> createState() => _AiCoachScreenState();
}

class _AiCoachScreenState extends State<AiCoachScreen> {
  int _seconds = 0;
  bool _isActive = true;
  int _reps = 12;
  late Timer _timer;
  String _feedback = 'KEEP YOUR BACK STRAIGHT';
  double _formAccuracy = 0.94;

  @override
  void initState() {
    super.initState();
    _startTimer();
    _simulateAiFeedback();
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_isActive) {
        setState(() => _seconds++);
      }
    });
  }

  void _simulateAiFeedback() {
    Timer.periodic(const Duration(seconds: 5), (timer) {
      if (!mounted) return;
      final feedbacks = [
        'PERFECT FORM',
        'SLOW DOWN ON THE DESCENT',
        'KEEP YOUR BACK STRAIGHT',
        'CORE ENGAGED',
        'FULL RANGE OF MOTION'
      ];
      setState(() {
        _feedback = feedbacks[_seconds % feedbacks.length];
        _formAccuracy = 0.85 + (0.15 * (1 - (_seconds % 10) / 10));
      });
    });
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  String _formatTime(int seconds) {
    final mins = (seconds / 60).floor().toString().padLeft(2, '0');
    final secs = (seconds % 60).toString().padLeft(2, '0');
    return '$mins:$secs';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // Camera Placeholder (Dark view with scan lines)
          _buildCameraPlaceholder(),

          // Overlay UI
          SafeArea(
            child: Column(
              children: [
                _buildTopBar(),
                const Spacer(),
                _buildAiFeedbackOverlay(),
                const SizedBox(height: 20),
                _buildBottomControls(),
              ],
            ),
          ),

          // AI Skeleton Points Placeholder
          _buildAiSkeletonOverlay(),
        ],
      ),
    );
  }

  Widget _buildCameraPlaceholder() {
    return Container(
      width: double.infinity,
      height: double.infinity,
      color: const Color(0xFF0A0A0A),
      child: Stack(
        children: [
          // Simulated scan lines
          ListView.builder(
            itemCount: 100,
            itemBuilder: (context, index) => Container(
              height: 1,
              color: Colors.white.withOpacity(0.02),
              margin: const EdgeInsets.symmetric(vertical: 4),
            ),
          ),
          Center(
            child: Icon(
              Icons.person_outline,
              size: 200,
              color: Colors.white.withOpacity(0.05),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTopBar() {
    return Padding(
      padding: const EdgeInsets.all(20.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          IconButton(
            icon: const Icon(Icons.close, color: Colors.white),
            onPressed: () => Navigator.of(context).pop(),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.6),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: const Color(0xFFFF4500).withOpacity(0.5)),
            ),
            child: Row(
              children: [
                const Icon(Icons.circle, color: Colors.red, size: 8),
                const SizedBox(width: 8),
                Text(
                  'AI ANALYZING',
                  style: GoogleFonts.oswald(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.1,
                  ),
                ),
              ],
            ),
          ),
          const Icon(Icons.flash_on, color: Colors.white),
        ],
      ),
    );
  }

  Widget _buildAiFeedbackOverlay() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: BrawlerzCard(
        color: Colors.black.withOpacity(0.7),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'AI FORM FEEDBACK',
                      style: TextStyle(
                        color: Colors.grey[400],
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 1.1,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _feedback,
                      style: GoogleFonts.oswald(
                        fontSize: 18,
                        color: _formAccuracy > 0.9 ? Colors.green : const Color(0xFFFF4500),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                CircularProgressIndicator(
                  value: _formAccuracy,
                  backgroundColor: Colors.grey[800],
                  color: _formAccuracy > 0.9 ? Colors.green : const Color(0xFFFF4500),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBottomControls() {
    return Container(
      padding: const EdgeInsets.all(30),
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E1E),
        borderRadius: const BorderRadius.vertical(top: Radius.circular(30)),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _metricColumn('TIME', _formatTime(_seconds)),
              _metricColumn('REPS', '$_reps'),
              _metricColumn('BPM', '142'),
            ],
          ),
          const SizedBox(height: 30),
          Row(
            children: [
              Expanded(
                child: ActionButton(
                  text: _isActive ? 'PAUSE' : 'RESUME',
                  isSecondary: true,
                  onPressed: () => setState(() => _isActive = !_isActive),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: ActionButton(
                  text: 'END SET',
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metricColumn(String label, String value) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            color: Colors.grey[500],
            fontSize: 12,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.1,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: GoogleFonts.oswald(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      ],
    );
  }

  Widget _buildAiSkeletonOverlay() {
    return Positioned.fill(
      child: IgnorePointer(
        child: CustomPaint(
          painter: _SkeletonPainter(),
        ),
      ),
    );
  }
}

class _SkeletonPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFFFF4500).withOpacity(0.5)
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    final dotPaint = Paint()
      ..color = const Color(0xFFFF4500)
      ..style = PaintingStyle.fill;

    // Draw some mock skeleton lines
    final center = Offset(size.width / 2, size.height / 2.5);
    canvas.drawCircle(center, 4, dotPaint); // Head
    canvas.drawLine(center, center.translate(0, 100), paint); // Torso
    canvas.drawLine(center.translate(-40, 20), center.translate(40, 20), paint); // Shoulders
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
