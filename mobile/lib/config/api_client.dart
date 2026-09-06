import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiClient {
  static const String baseUrl = 'http://localhost:8000';

  static Future<Map<String, dynamic>> authenticateWithGoogle(String idToken) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/google'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'idToken': idToken,
        }),
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () => throw Exception('Timeout na comunicação com o servidor'),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else if (response.statusCode == 401) {
        throw Exception('Token inválido ou expirado');
      } else if (response.statusCode == 400) {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Erro ao processar token');
      } else {
        throw Exception('Erro no servidor (${response.statusCode})');
      }
    } on http.ClientException catch (e) {
      throw Exception('Erro de conexão: ${e.message}');
    } catch (e) {
      rethrow;
    }
  }
}
