import 'package:flutter/material.dart';
import 'package:google_sign_in/google_sign_in.dart';
import '../config/api_client.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  late GoogleSignIn _googleSignIn;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _googleSignIn = GoogleSignIn(
      scopes: ['email', 'profile'],
      clientId: null,
    );
  }

  Future<void> _handleGoogleSignIn() async {
    if (_isLoading) return;

    setState(() => _isLoading = true);

    try {
      final result = await _googleSignIn.signIn();
      if (result == null) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Login cancelado')),
          );
        }
        setState(() => _isLoading = false);
        return;
      }

      final auth = await result.authentication;
      final idToken = auth.idToken;

      if (idToken == null) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Erro ao obter token do Google')),
          );
        }
        setState(() => _isLoading = false);
        return;
      }

      final response = await ApiClient.authenticateWithGoogle(idToken);

      if (response['success'] == true && mounted) {
        Navigator.pushReplacementNamed(context, '/sobre');
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(response['message'] ?? 'Erro desconhecido')),
        );
      }
    } on Exception catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro: ${e.toString()}')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.analytics_outlined, size: 80, color: Color(0xFF60A5FA)),
              const SizedBox(height: 24),
              const Text(
                'RentMaster',
                style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Color(0xFF1F2937)),
              ),
              const SizedBox(height: 12),
              const Text(
                "O 'Moneyball' dos aluguéis no Distrito Federal. Avalie preços com Inteligência Artificial.",
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, color: Colors.grey),
              ),
              const SizedBox(height: 48),
              _isLoading
                  ? const SizedBox(
                      height: 50,
                      child: Center(
                        child: CircularProgressIndicator(
                          valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF60A5FA)),
                        ),
                      ),
                    )
                  : ElevatedButton.icon(
                      onPressed: _handleGoogleSignIn,
                      icon: const Icon(Icons.login, color: Colors.white),
                      label: const Text('Continuar com o Google'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF60A5FA),
                        foregroundColor: Colors.white,
                        minimumSize: const Size(double.infinity, 50),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                    ),
              const SizedBox(height: 16),
              TextButton(
                onPressed: () => Navigator.pushNamed(context, '/sobre'),
                child: const Text('Conheça o projeto', style: TextStyle(color: Color(0xFF60A5FA))),
              ),
              const SizedBox(height: 48),
              const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.security, size: 16, color: Colors.grey),
                  SizedBox(width: 8),
                  Text('Dados seguros e processados com IA', style: TextStyle(fontSize: 12, color: Colors.grey)),
                ],
              )
            ],
          ),
        ),
      ),
    );
  }
}
