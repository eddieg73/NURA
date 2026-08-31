import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:brawlerz_box/features/auth/auth_repository.dart';
import 'package:brawlerz_box/shared/widgets/action_button.dart';

class SplashScreen extends ConsumerStatefulWidget {
  const SplashScreen({super.key});

  @override
  ConsumerState<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends ConsumerState<SplashScreen> {
  bool _checkingSession = true;

  @override
  void initState() {
    super.initState();
    Future.microtask(_restoreSession);
  }

  Future<void> _restoreSession() async {
    final repository = ref.read(authRepositoryProvider);
    final hasSession = await repository.hasSession();
    if (hasSession) {
      try {
        await repository.currentUser();
        if (mounted) {
          context.go('/dashboard');
          return;
        }
      } catch (_) {
        await repository.logout();
      }
    }
    if (mounted) setState(() => _checkingSession = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF1E1E1E), Color(0xFF121212)],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Spacer(),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'BRAWLERZ',
                      style: GoogleFonts.oswald(
                        fontSize: 48,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                        letterSpacing: 2,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFF4500),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        'BOX',
                        style: GoogleFonts.oswald(
                          fontSize: 48,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                Text(
                  'YOUR AI COACH. YOUR GYM. YOUR ECOSYSTEM.',
                  textAlign: TextAlign.center,
                  style: GoogleFonts.oswald(
                    fontSize: 18,
                    color: Colors.grey[400],
                    letterSpacing: 1.5,
                  ),
                ),
                const Spacer(),
                if (_checkingSession)
                  const Padding(
                    padding: EdgeInsets.only(bottom: 40),
                    child: CircularProgressIndicator(),
                  )
                else ...[
                  ActionButton(
                    text: 'Get Started',
                    onPressed: () => context.go('/login'),
                  ),
                  const SizedBox(height: 16),
                  TextButton(
                    onPressed: () => context.go('/login'),
                    child: Text(
                      'SIGN IN',
                      style: GoogleFonts.oswald(
                        color: Colors.white,
                        letterSpacing: 1.2,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(height: 40),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
