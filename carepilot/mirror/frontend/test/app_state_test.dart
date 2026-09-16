import 'package:flutter_test/flutter_test.dart';
import 'package:carepilot/state/app_state.dart';
import 'package:carepilot/api.dart';

void main() {
  test('AppState selectTab notifies and updates index', () {
    final app = AppState();
    var notified = 0;
    app.addListener(() => notified++);

    expect(app.selectedIndex, 0);
    app.selectTab(2);
    expect(app.selectedIndex, 2);
    expect(notified, 1);

    app.selectTab(2); // no-op
    expect(notified, 1);
  });

  test('AppState setRole syncs Api.role', () {
    final app = AppState();
    expect(Api.role, 'read_only');

    app.setRole('provider');
    expect(app.role, 'provider');
    expect(Api.role, 'provider');
  });
}
