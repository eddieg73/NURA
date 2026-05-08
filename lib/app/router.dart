import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// Features
import 'package:brawlerz_box/features/auth/splash_screen.dart';
import 'package:brawlerz_box/features/auth/login_screen.dart';
import 'package:brawlerz_box/features/dashboard/dashboard_screen.dart';
import 'package:brawlerz_box/features/qr_access/qr_screen.dart';
import 'package:brawlerz_box/features/ai_coach/ai_coach_screen.dart';
import 'package:brawlerz_box/features/workouts/workouts_screen.dart';
import 'package:brawlerz_box/features/classes/classes_screen.dart';
import 'package:brawlerz_box/features/nutrition/nutrition_screen.dart';
import 'package:brawlerz_box/features/supplements/supplements_screen.dart';
import 'package:brawlerz_box/features/progress/progress_screen.dart';
import 'package:brawlerz_box/features/integrations/integrations_screen.dart';
import 'package:brawlerz_box/features/admin/admin_dashboard_screen.dart';
import 'package:brawlerz_box/shared/widgets/scaffold_with_navbar.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      ShellRoute(
        builder: (context, state, child) => ScaffoldWithNavBar(child: child),
        routes: [
          GoRoute(
            path: '/dashboard',
            builder: (context, state) => const DashboardScreen(),
          ),
          GoRoute(
            path: '/workouts',
            builder: (context, state) => const WorkoutsScreen(),
          ),
          GoRoute(
            path: '/qr',
            builder: (context, state) => const QrScreen(),
          ),
          GoRoute(
            path: '/progress',
            builder: (context, state) => const ProgressScreen(),
          ),
          GoRoute(
            path: '/profile',
            builder: (context, state) => const ProfileScreen(),
          ),
        ],
      ),
      GoRoute(
        path: '/ai-coach',
        builder: (context, state) => const AiCoachScreen(),
      ),
      GoRoute(
        path: '/classes',
        builder: (context, state) => const ClassesScreen(),
      ),
      GoRoute(
        path: '/nutrition',
        builder: (context, state) => const NutritionScreen(),
      ),
      GoRoute(
        path: '/supplements',
        builder: (context, state) => const SupplementsScreen(),
      ),
      GoRoute(
        path: '/integrations',
        builder: (context, state) => const IntegrationsScreen(),
      ),
      GoRoute(
        path: '/admin',
        builder: (context, state) => const AdminDashboardScreen(),
      ),
    ],
  );
});

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          ListTile(
            leading: const Icon(Icons.admin_panel_settings),
            title: const Text('Admin Dashboard'),
            onTap: () => context.push('/admin'),
          ),
          ListTile(
            leading: const Icon(Icons.settings),
            title: const Text('Integrations'),
            onTap: () => context.push('/integrations'),
          ),
          ListTile(
            leading: const Icon(Icons.restaurant),
            title: const Text('Nutrition'),
            onTap: () => context.push('/nutrition'),
          ),
          ListTile(
            leading: const Icon(Icons.shopping_bag),
            title: const Text('Supplements'),
            onTap: () => context.push('/supplements'),
          ),
          ListTile(
            leading: const Icon(Icons.calendar_month),
            title: const Text('Class Booking'),
            onTap: () => context.push('/classes'),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.logout),
            title: const Text('Logout'),
            onTap: () => context.go('/login'),
          ),
        ],
      ),
    );
  }
}
