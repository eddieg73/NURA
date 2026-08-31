import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:nura_medical/app.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    FlutterSecureStorage.setMockInitialValues(<String, String>{});
  });

  testWidgets('secure login surface renders with clinical safety boundary',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(child: NuraMedicalApp()),
    );
    await tester.pumpAndSettle();

    expect(find.text('NURA Medical'), findsOneWidget);
    expect(find.text('Sign in securely'), findsOneWidget);
    expect(find.textContaining('Clinical outputs are drafts'), findsOneWidget);
    expect(find.textContaining('emergency communication'), findsOneWidget);
  });
}
