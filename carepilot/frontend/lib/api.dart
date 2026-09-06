import 'dart:convert';
import 'package:http/http.dart' as http;

/// CarePilot API client — points at the FastAPI backend.
/// Role header drives RBAC on the server (set per screen; provider/nurse for writes).
const String kApi = String.fromEnvironment('CAREPILOT_API', defaultValue: 'http://localhost:8000');

class Api {
  static String role = 'read_only';

  static Uri _u(String path) => Uri.parse('$kApi$path');

  static Future<Map<String, dynamic>> get(String path) async {
    final r = await http.get(_u(path), headers: {'X-Role': role});
    if (r.statusCode >= 400) throw Exception('GET $path -> ${r.statusCode}: ${r.body}');
    return jsonDecode(r.body) as Map<String, dynamic>;
  }

  static Future<Map<String, dynamic>> post(String path, Map<String, dynamic> body) async {
    final r = await http.post(_u(path), headers: {'X-Role': role, 'Content-Type': 'application/json'}, body: jsonEncode(body));
    if (r.statusCode >= 400) throw Exception('POST $path -> ${r.statusCode}: ${r.body}');
    return jsonDecode(r.body) as Map<String, dynamic>;
  }
}
