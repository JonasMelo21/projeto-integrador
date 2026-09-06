import 'package:flutter/material.dart';
import 'screens/login_page.dart';
import 'screens/sobre_page.dart';

void main() {
  runApp(const RentMasterApp());
}

class RentMasterApp extends StatelessWidget {
  const RentMasterApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RentMaster',
      theme: ThemeData(
        scaffoldBackgroundColor: Colors.white,
        primaryColor: const Color(0xFF60A5FA), // Azul Pastel
        textTheme: const TextTheme(
          bodyMedium: TextStyle(color: Color(0xFF1F2937)), // Cinza Escuro
        ),
      ),
      initialRoute: '/login',
      routes: {
        '/login': (context) => const LoginPage(),
        '/sobre': (context) => const SobrePage(),
      },
    );
  }
}
