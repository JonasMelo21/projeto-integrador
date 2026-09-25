import { useEffect, useState } from 'react';
import { View, FlatList, StyleSheet, ActivityIndicator, Pressable, SafeAreaView } from 'react-native';

import { PropertyCard, type PropertyCardProps } from '@/components/property-card';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { supabase } from '@/lib/supabase';
import { useRouter } from 'expo-router';
import { MaterialCommunityIcons } from '@expo/vector-icons';

type Property = PropertyCardProps;

export default function HomeScreen() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const router = useRouter();

  // Verificar autenticação na primeira renderização
  useEffect(() => {
    const checkAuth = async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        router.replace('/');
        return;
      }

      loadProperties();
    };

    checkAuth();

    // Escuta mudanças de autenticação
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event, session) => {
      if (!session && event !== 'SIGNED_IN') {
        router.replace('/');
      }
    });

    return () => {
      subscription?.unsubscribe();
    };
  }, []);

  const loadProperties = async () => {
    try {
      setLoading(true);
      setError(null);

      const { data, error: fetchError } = await supabase
        .from('imoveis_classificados')
        .select(
          'id_hex, id_imovel, titulo, preco, bairro, quartos, vagas, area, imagem, url, ml_label'
        )
        .limit(50);

      if (fetchError) {
        throw fetchError;
      }

      if (data) {
        // Mapear dados do banco para o formato do PropertyCard
        const formattedProperties: Property[] = data.map((item: any) => ({
          id_imovel: item.id_imovel || '',
          id_hex: item.id_hex,
          titulo: item.titulo || 'Sem título',
          preco: parseFloat(item.preco) || 0,
          bairro: item.bairro || 'Brasília',
          quartos: item.quartos ? parseInt(item.quartos) : null,
          vagas: item.vagas ? parseInt(item.vagas) : null,
          area: item.area ? parseFloat(item.area) : null,
          imagem: item.imagem,
          url: item.url || '',
          ml_label: item.ml_label || 'Justo',
        }));

        setProperties(formattedProperties);
      }
    } catch (err: any) {
      console.error('Erro ao carregar imóveis:', err);
      setError(err.message || 'Erro ao carregar os imóveis');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    loadProperties();
  };

  const handleLogout = async () => {
    try {
      await supabase.auth.signOut();
      router.replace('/');
    } catch (err) {
      console.error('Erro ao fazer logout:', err);
    }
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2563eb" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <ThemedText type="title" style={styles.headerTitle}>
            RentMaster
          </ThemedText>
          <ThemedText type="small" themeColor="textSecondary">
            {properties.length} imóveis disponíveis
          </ThemedText>
        </View>
        <Pressable
          onPress={handleLogout}
          style={({ pressed }) => [styles.logoutButton, pressed && styles.logoutButtonPressed]}
        >
          <MaterialCommunityIcons name="logout" size={20} color="#ef4444" />
        </Pressable>
      </View>

      {/* Content */}
      {error ? (
        <View style={styles.errorContainer}>
          <ThemedText type="default" style={styles.errorText}>
            ❌ {error}
          </ThemedText>
          <Pressable onPress={handleRefresh} style={styles.retryButton}>
            <ThemedText type="small" style={styles.retryButtonText}>
              Tentar Novamente
            </ThemedText>
          </Pressable>
        </View>
      ) : properties.length === 0 ? (
        <View style={styles.emptyContainer}>
          <ThemedText type="default">Nenhum imóvel encontrado</ThemedText>
        </View>
      ) : (
        <FlatList
          data={properties}
          renderItem={({ item }) => <PropertyCard {...item} />}
          keyExtractor={(item) => item.id_hex}
          contentContainerStyle={styles.listContent}
          scrollIndicatorInsets={{ right: 1 }}
          refreshing={refreshing}
          onRefresh={handleRefresh}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121418',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#121418',
  },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#1e293b',
  },
  headerContent: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#f8fafc',
  },
  logoutButton: {
    padding: 8,
    borderRadius: 8,
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
  },
  logoutButtonPressed: {
    opacity: 0.7,
  },
  listContent: {
    paddingHorizontal: 12,
    paddingVertical: 12,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
    gap: 16,
  },
  errorText: {
    color: '#ef4444',
    textAlign: 'center',
  },
  retryButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: '#2563eb',
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#ffffff',
    fontWeight: 'bold',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
