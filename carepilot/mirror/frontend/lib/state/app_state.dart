import 'package:flutter/foundation.dart';
import '../api.dart';

/// App-level shell state (nav + API role). Screens stay thin consumers.
class AppState extends ChangeNotifier {
  int _selectedIndex = 0;
  String _role = 'read_only';

  AppState() {
    Api.role = _role;
  }

  int get selectedIndex => _selectedIndex;
  String get role => _role;

  void selectTab(int index) {
    if (index == _selectedIndex) return;
    _selectedIndex = index;
    notifyListeners();
  }

  void setRole(String role) {
    if (role == _role) return;
    _role = role;
    Api.role = role;
    notifyListeners();
  }
}
