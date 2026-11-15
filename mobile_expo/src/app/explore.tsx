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
            O RentMaster foi criado para combater a assimetria de informações no mercado imobiliário. Nossa missão não é vender imóveis, mas sim usar inteligência de dados para dizer se o preço anunciado é justo, caro demais ou barato demais pelo que o imóvel realmente oferece.
          </Text>
        </View>

        {/* Benefícios */}
        <View style={styles.cardsWrapper}>
          <View style={styles.card}>
            <View style={styles.iconContainer}>
              <MaterialCommunityIcons name="eye-outline" size={28} color="#60a5fa" />
            </View>
            <View style={styles.cardContent}>
              <Text style={styles.cardTitle}>Transparência Real</Text>
              <Text style={styles.cardText}>
                Saiba instantaneamente se o valor cobrado por um imóvel está alinhado com as características que ele possui e a região onde se encontra.
              </Text>
            </View>
          </View>

          <View style={styles.card}>
            <View style={styles.iconContainer}>
              <MaterialCommunityIcons name="clock-outline" size={28} color="#60a5fa" />
            </View>
            <View style={styles.cardContent}>
              <Text style={styles.cardTitle}>Economia de Tempo</Text>
              <Text style={styles.cardText}>
                Pare de fazer cálculos complexos ou cruzar abas de navegador. Nossa inteligência audita milhares de imóveis para você.
              </Text>
            </View>
          </View>

          <View style={styles.card}>
            <View style={styles.iconContainer}>
              <MaterialCommunityIcons name="shield-check-outline" size={28} color="#60a5fa" />
            </View>
            <View style={styles.cardContent}>
              <Text style={styles.cardTitle}>Decisão Segura</Text>
              <Text style={styles.cardText}>
                Tenha os dados necessários na palma da mão para negociar melhor e nunca pagar mais do que um imóvel realmente vale.
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
