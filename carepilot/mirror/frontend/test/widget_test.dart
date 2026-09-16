import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:carepilot/main.dart';
import 'package:carepilot/state/app_state.dart';

void main() {
  testWidgets('RootShell shows Command nav destination', (tester) async {
    await tester.pumpWidget(
      MultiProvider(
        providers: [ChangeNotifierProvider(create: (_) => AppState())],
        child: const MaterialApp(home: RootShell()),
      ),
    );

    expect(find.text('Command'), findsOneWidget);
    expect(find.text('Queue'), findsOneWidget);
  });
}
