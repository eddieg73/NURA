// The NURA smoke test — the 5-tab shell renders + the tabs switch.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:nura_medical/main.dart';

void main() {
  testWidgets('The 5-tab shell renders and the tabs switch', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());
    await tester.pump();

    // The navigation bar renders with the 5 destinations.
    expect(find.byType(NavigationBar), findsOneWidget);
    expect(find.text('Scribe'), findsWidgets);
    expect(find.text('Clinical'), findsWidgets);

    // The switch to the Ops tab.
    await tester.tap(find.text('Ops'));
    await tester.pumpAndSettle();
    expect(find.text('📋 NURA Ops — the back office'), findsOneWidget);

    // The switch to the Account tab.
    await tester.tap(find.text('Account'));
    await tester.pumpAndSettle();
    expect(find.text('The license gate'), findsOneWidget);
  });
}
