import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'app_appstore.dart';
import 'core/config/app_config.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  AppConfig.validate();
  runApp(const ProviderScope(child: NuraMedicalAppStoreApp()));
}
