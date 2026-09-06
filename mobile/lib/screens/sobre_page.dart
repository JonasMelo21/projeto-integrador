import 'package:flutter/material.dart';

class SobrePage extends StatelessWidget {
  const SobrePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Color(0xFF1F2937)),
        title: const Text('Sobre o RentMaster', style: TextStyle(color: Color(0xFF1F2937))),
      ),
      body: ListView(
        padding: const EdgeInsets.all(24.0),
        children: [
          const Text(
            'O RentMaster atua como um mediador imparcial para combater a assimetria de informações no mercado imobiliário, utilizando algoritmos para identificar se um aluguel é justo, caro ou uma barganha.',
            style: TextStyle(fontSize: 16, height: 1.5, color: Color(0xFF1F2937)),
          ),
          const SizedBox(height: 32),
          _buildFeatureCard(Icons.storage, 'Pipeline de Dados', 'Monitoramento contínuo do mercado imobiliário em tempo real.'),
          const SizedBox(height: 16),
          _buildFeatureCard(Icons.auto_awesome, 'Machine Learning', 'Precificação preditiva utilizando modelos avançados de Random Forest.'),
          const SizedBox(height: 16),
          _buildFeatureCard(Icons.chat_bubble_outline, 'Assistente Virtual', 'Interaja com os dados do mercado usando linguagem natural.'),
          const SizedBox(height: 48),
          const Center(child: Text('Desenvolvido como Projeto Integrador IV', style: TextStyle(fontSize: 12, color: Colors.grey))),
        ],
      ),
    );
  }

  Widget _buildFeatureCard(IconData icon, String title, String subtitle) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(color: const Color.fromRGBO(0, 0, 0, 0.05), blurRadius: 10, offset: const Offset(0, 4)),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(8)),
            child: Icon(icon, color: const Color(0xFF60A5FA)),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                const SizedBox(height: 4),
                Text(subtitle, style: const TextStyle(color: Colors.grey, fontSize: 14)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
