import React from 'react';
import { View, Text, StyleSheet, ScrollView, SafeAreaView } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';

export default function ExploreScreen() {
  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        {/* Cabeçalho */}
        <View style={styles.header}>
          <Text style={styles.eyebrow}>O MONEYBALL DO ALUGUEL</Text>
          <Text style={styles.title}>RentMaster</Text>
          <Text style={styles.description}>
            Utilizamos Inteligência Artificial para combater a assimetria de informações no mercado imobiliário do DF. Descubra se um aluguel é justo, caro ou uma verdadeira barganha.
          </Text>
        </View>

        {/* Cards de Tecnologia */}
        <View style={styles.cardsWrapper}>
          <View style={styles.card}>
            <View style={styles.iconContainer}>
              <MaterialCommunityIcons name="database-search" size={28} color="#60a5fa" />
            </View>
            <View style={styles.cardContent}>
              <Text style={styles.cardTitle}>Pipeline de Dados</Text>
              <Text style={styles.cardText}>
                Arquitetura Medallion processando e refinando milhares de imóveis em tempo real.
              </Text>
            </View>
          </View>

          <View style={styles.card}>
            <View style={styles.iconContainer}>
              <MaterialCommunityIcons name="brain" size={28} color="#60a5fa" />
            </View>
            <View style={styles.cardContent}>
              <Text style={styles.cardTitle}>Machine Learning</Text>
              <Text style={styles.cardText}>
                Modelos preditivos Random Forest que identificam anomalias e garantem uma precificação justa.
              </Text>
            </View>
          </View>

          <View style={styles.card}>
            <View style={styles.iconContainer}>
              <MaterialCommunityIcons name="robot-outline" size={28} color="#60a5fa" />
            </View>
            <View style={styles.cardContent}>
              <Text style={styles.cardTitle}>Assistente Vanna AI</Text>
              <Text style={styles.cardText}>
                Inteligência conversacional integrada para analisar o mercado através de linguagem natural.
              </Text>
            </View>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#121418',
  },
  container: {
    padding: 24,
    paddingBottom: 40,
  },
  header: {
    marginBottom: 32,
    marginTop: 20,
  },
  eyebrow: {
    color: '#60a5fa',
    fontSize: 13,
    fontWeight: '700',
    letterSpacing: 2,
    marginBottom: 8,
  },
  title: {
    color: '#f8fafc',
    fontSize: 40,
    fontWeight: '800',
    marginBottom: 16,
  },
  description: {
    color: '#94a3b8',
    fontSize: 16,
    lineHeight: 24,
  },
  cardsWrapper: {
    gap: 16,
  },
  card: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#334155',
  },
  iconContainer: {
    width: 50,
    height: 50,
    borderRadius: 12,
    backgroundColor: '#0f172a',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  cardContent: {
    flex: 1,
  },
  cardTitle: {
    color: '#f8fafc',
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 4,
  },
  cardText: {
    color: '#94a3b8',
    fontSize: 14,
    lineHeight: 20,
  },
});
