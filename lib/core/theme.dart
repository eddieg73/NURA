import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class BrawlerzColors {
  static const Color background = Color(0xFF121212);
  static const Color surface = Color(0xFF1E1E1E);
  static const Color primary = Color(0xFFFF4500); // Red-orange accent
  static const Color textPrimary = Colors.white;
  static const Color textSecondary = Colors.grey;
}

class BrawlerzTheme {
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: BrawlerzColors.background,
      colorScheme: const ColorScheme.dark(
        primary: BrawlerzColors.primary,
        surface: BrawlerzColors.surface,
        onSurface: BrawlerzColors.textPrimary,
        onPrimary: Colors.white,
      ),
      textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme).copyWith(
        displayLarge: GoogleFonts.oswald(
          fontSize: 32,
          fontWeight: FontWeight.bold,
          color: BrawlerzColors.textPrimary,
        ),
        displayMedium: GoogleFonts.oswald(
          fontSize: 24,
          fontWeight: FontWeight.bold,
          color: BrawlerzColors.textPrimary,
        ),
        titleLarge: GoogleFonts.oswald(
          fontSize: 20,
          fontWeight: FontWeight.bold,
          color: BrawlerzColors.textPrimary,
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: BrawlerzColors.background,
        elevation: 0,
        centerTitle: false,
      ),
      cardTheme: CardTheme(
        color: BrawlerzColors.surface,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: BrawlerzColors.primary,
          foregroundColor: Colors.white,
          textStyle: GoogleFonts.oswald(fontWeight: FontWeight.bold),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
      ),
    );
  }
}
