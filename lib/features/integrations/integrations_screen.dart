import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:brawlerz_box/shared/widgets/brawlerz_card.dart';

class IntegrationsScreen extends StatelessWidget {
  const IntegrationsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'INTEGRATIONS',
          style: GoogleFonts.oswald(fontWeight: FontWeight.bold),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _buildSectionHeader('HEALTH & WEARABLES'),
          _buildIntegrationTile('Apple Health', 'Connected', Icons.favorite, Colors.red, true),
          _buildIntegrationTile('Garmin', 'Connect Account', Icons.watch, Colors.blue, false),
          _buildIntegrationTile('WHOOP', 'Connect Account', Icons.bolt, Colors.white, false),

          const SizedBox(height: 32),
          _buildSectionHeader('FOOD & NUTRITION'),
          _buildIntegrationTile('Instacart', 'Connected', Icons.shopping_basket, Colors.orange, true),
          _buildIntegrationTile('Amazon Whole Foods', 'Connect Account', Icons.shopping_cart, Colors.green, false),
          _buildIntegrationTile('DoorDash', 'Connect Account', Icons.delivery_dining, Colors.redAccent, false),
          _buildIntegrationTile('Uber Eats', 'Connect Account', Icons.restaurant, Colors.black, false),

          const SizedBox(height: 32),
          _buildSectionHeader('GYM SYSTEMS'),
          _buildIntegrationTile('Mindbody', 'Connected', Icons.self_improvement, Colors.deepPurple, true),

          const SizedBox(height: 40),
          const Text(
            'Integrations allow Brawlerz Box to provide personalized recommendations based on your activity, recovery, and shopping habits.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey, fontSize: 12),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: Text(
        title,
        style: GoogleFonts.oswald(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          letterSpacing: 1.2,
          color: const Color(0xFFFF4500),
        ),
      ),
    );
  }

  Widget _buildIntegrationTile(String name, String status, IconData icon, Color iconColor, bool isConnected) {
    return Padding(
      padding: const EdgeInsets.bottom(12.0),
      child: BrawlerzCard(
        onTap: () {},
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: iconColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: iconColor, size: 24),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
                  Text(
                    status,
                    style: TextStyle(
                      color: isConnected ? Colors.green : Colors.grey,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
            isConnected
              ? const Icon(Icons.check_circle, color: Colors.green, size: 20)
              : const Icon(Icons.add_circle_outline, color: Colors.grey, size: 20),
          ],
        ),
      ),
    );
  }
}
