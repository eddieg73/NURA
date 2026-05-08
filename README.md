# Brawlerz Box - AI Powered Fitness Ecosystem

Brawlerz Box is a premium, AI-powered fitness, boxing, wellness, nutrition, and recovery ecosystem. This Flutter MVP demonstrates the core member experience and business dashboard with a high-performance, dark-athletic aesthetic.

## 🚀 MVP Features

### Member Experience
- **Premium Dashboard:** Personalized readiness score (HRV, Sleep) and daily workout focus.
- **QR Gym Access:** Seamless 24/7 facility entry via digital member ID.
- **AI Coach:** Mock computer vision form analysis for squats and boxing drills.
- **Workout Library:** Curated boxing, strength, and HIIT programs.
- **Class Booking:** Real-time reservation system for studio classes.
- **Nutrition & Macros:** Daily calorie tracking with meal breakdown and grocery integration placeholders.
- **Supplements Store:** AI-driven personalized supplement recommendations.
- **Progress Tracking:** Interactive charts for strength gains and body composition.
- **Integrations:** Mock connection interfaces for Apple Health, WHOOP, Garmin, and delivery services.

### Business/Admin View
- **Executive Dashboard:** Real-time metrics for total members, check-ins, and revenue.
- **Growth Analytics:** Visual representation of revenue and membership trends.
- **Operations:** Class attendance monitoring and facility status.

## 🛠 Tech Stack
- **Framework:** Flutter 3.x (Dart 3.x)
- **State Management:** Riverpod
- **Navigation:** GoRouter
- **Charts:** fl_chart
- **UI:** Custom Material 3 Dark Theme with Google Fonts (Oswald & Inter)
- **Architecture:** Clean Architecture (Feature-based modular structure)

## 📁 Project Structure
```
lib/
  app/          # Global configuration & routing
  core/         # Theming, constants, and utilities
  features/     # Feature-based modules (UI + logic)
  shared/       # Reusable widgets, models, and repositories
```

## 🏗 Setup Instructions
1. Ensure you have the [Flutter SDK](https://docs.flutter.dev/get-started/install) installed.
2. Clone the repository.
3. Run `flutter pub get` to install dependencies.
4. Run `flutter run` (supports iOS, Android, and Web).

## 🗺 Future Roadmap & API Integration

### TODO: Wearable Integration
- [ ] Implement `HealthKit` (iOS) and `Google Fit` (Android) services.
- [ ] Connect `WHOOP` and `Garmin` Webhooks/APIs for real-time recovery data.

### TODO: AI & Computer Vision
- [ ] Replace mock AI overlay with `google_ml_kit` or custom TFLite models for pose estimation.
- [ ] Implement backend analysis for complex boxing drill form feedback.

### TODO: Commerce & Logistics
- [ ] Integrate `Stripe` for supplement purchases and membership billing.
- [ ] Connect `Instacart` and `Amazon` APIs for automated grocery ordering based on nutrition plans.

### TODO: Facility Access
- [ ] Connect QR system with physical access control hardware (IoT integration).

---
*Disclaimer: This is an MVP prototype for investor demonstration purposes. Medical, supplement, and health claims are for UI/UX demonstration only.*
