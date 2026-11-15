import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  KeyboardAvoidingView,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import type { KeyboardTypeOptions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

import PropertyCard from '@/components/property-card';
import { supabase } from '@/lib/supabase';

type Property = {
  id_imovel?: string | number | null;
  id?: string | number | null;
  titulo?: string | null;
  preco?: number | string | null;
  valor_aluguel?: number | string | null;
  area?: number | string | null;
  area_m2?: number | string | null;
  bairro?: string | null;
  local_bairro?: string | null;
  url?: string | null;
  imagem?: string | null;
  ml_label?: string | null;
  classificacao_preco?: string | null;
};

type ClassificationFilter = 'Todos' | 'Justo' | 'Caro' | 'Barato';

type PropertyFilters = {
  neighborhood: string;
  maxPrice: string;
  minArea: string;
  classification: ClassificationFilter;
};

const EMPTY_FILTERS: PropertyFilters = {
  neighborhood: '',
  maxPrice: '',
  minArea: '',
  classification: 'Todos',
};

function parseNumericValue(value: number | string | null | undefined) {
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : null;
  }

  if (!value) {
    return null;
  }

  const normalized = value
    .replace(/[^\d,.-]/g, '')
    .replace(/\.(?=.*[,])/g, '')
    .replace(',', '.');
  const parsed = Number(normalized);

  return Number.isFinite(parsed) ? parsed : null;
}

function normalizeClassification(value: string | null | undefined) {
  return value?.trim().toLocaleLowerCase('pt-BR').replace(/^preço\s+/, '') ?? '';
}

export default function HomeScreen() {
  const router = useRouter();
  const [properties, setProperties] = useState<Property[]>([]);
  const [isLoading, setIsLoading] = useState(Boolean(supabase));
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [isFilterModalVisible, setIsFilterModalVisible] = useState(false);
  const [isNeighborhoodDropdownOpen, setIsNeighborhoodDropdownOpen] = useState(false);
  const [draftFilters, setDraftFilters] = useState<PropertyFilters>(EMPTY_FILTERS);
  const [appliedFilters, setAppliedFilters] = useState<PropertyFilters>(EMPTY_FILTERS);
  const [errorMessage, setErrorMessage] = useState<string | null>(
    supabase ? null : 'A conexão com o serviço de imóveis não está configurada.'
  );

  const filteredProperties = properties.filter((property) => {
    const neighborhood = appliedFilters.neighborhood.trim().toLocaleLowerCase('pt-BR');
    const propertyNeighborhood = (property.bairro ?? property.local_bairro ?? '')
      .trim()
      .toLocaleLowerCase('pt-BR');
    if (neighborhood && !propertyNeighborhood.includes(neighborhood)) {
      return false;
    }

    if (appliedFilters.maxPrice) {
      const maxPrice = parseNumericValue(appliedFilters.maxPrice);
      const propertyPrice = parseNumericValue(property.preco ?? property.valor_aluguel);
      if (maxPrice !== null && (propertyPrice === null || propertyPrice > maxPrice)) {
        return false;
      }
    }

    if (appliedFilters.minArea) {
      const minArea = parseNumericValue(appliedFilters.minArea);
      const propertyArea = parseNumericValue(property.area ?? property.area_m2);
      if (minArea !== null && (propertyArea === null || propertyArea < minArea)) {
        return false;
      }
    }

    return (
      appliedFilters.classification === 'Todos' ||
      normalizeClassification(property.ml_label ?? property.classificacao_preco) ===
        appliedFilters.classification.toLocaleLowerCase('pt-BR')
    );
  });

  const neighborhoods = useMemo(() => {
    const distinctNeighborhoods = new Map<string, string>();

    properties.forEach((property) => {
      const neighborhood = (property.bairro ?? property.local_bairro ?? '').trim();
      const key = neighborhood.toLocaleLowerCase('pt-BR');
      if (key && !distinctNeighborhoods.has(key)) {
        distinctNeighborhoods.set(key, neighborhood);
      }
    });

    return Array.from(distinctNeighborhoods.values()).sort((first, second) =>
      first.localeCompare(second, 'pt-BR')
    );
  }, [properties]);

  const activeFiltersCount = [
    appliedFilters.neighborhood.trim(),
    appliedFilters.maxPrice.trim(),
    appliedFilters.minArea.trim(),
    appliedFilters.classification !== 'Todos',
  ].filter(Boolean).length;

  const loadProperties = useCallback(async () => {
    if (!supabase) {
      return;
    }

    try {
      const { data, error } = await supabase
        .from('imoveis_classificados')
        .select('*');

      if (error) {
        console.error('Erro ao carregar imóveis:', error);
        setProperties([]);
        setErrorMessage('Não foi possível carregar os imóveis. Tente novamente.');
      } else {
        setProperties(data ?? []);
        setErrorMessage(null);
      }
    } catch (error) {
      console.error('Falha inesperada ao carregar imóveis:', error);
      setProperties([]);
      setErrorMessage('Não foi possível carregar os imóveis. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void Promise.resolve().then(loadProperties);
  }, [loadProperties]);

  async function handleLogout() {
    if (isLoggingOut) {
      return;
    }

    setIsLoggingOut(true);

    try {
      if (supabase) {
        const { error } = await supabase.auth.signOut();
        if (error) {
          throw error;
        }
      }

      router.replace('/');
    } catch (error) {
      console.error('Erro ao sair da conta:', error);
      Alert.alert('Não foi possível sair', 'Tente novamente.');
    } finally {
      setIsLoggingOut(false);
    }
  }

  function updateDraftFilter<K extends keyof PropertyFilters>(
    key: K,
    value: PropertyFilters[K]
  ) {
    setDraftFilters((current) => ({ ...current, [key]: value }));
  }

  function openFilters() {
    setDraftFilters(appliedFilters);
    setIsNeighborhoodDropdownOpen(false);
    setIsFilterModalVisible(true);
  }

  function applyFilters() {
    setAppliedFilters(draftFilters);
    setIsNeighborhoodDropdownOpen(false);
    setIsFilterModalVisible(false);
  }

  function renderFilterInput(
    label: string,
    placeholder: string,
    value: string,
    onChangeText: (text: string) => void,
    keyboardType: KeyboardTypeOptions = 'default'
  ) {
    return (
      <View style={styles.filterField}>
        <Text style={styles.filterLabel}>{label}</Text>
        <TextInput
          accessibilityLabel={label}
          keyboardType={keyboardType}
          onChangeText={onChangeText}
          placeholder={placeholder}
          placeholderTextColor="#64748b"
          style={styles.filterInput}
          value={value}
        />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <FlatList
        data={filteredProperties}
        keyExtractor={(item, index) => String(item.id_imovel ?? item.id ?? index)}
        contentContainerStyle={[styles.listContent, { paddingBottom: 100 }]}
        showsVerticalScrollIndicator={false}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
        ListHeaderComponent={
          <View>
            <View style={styles.header}>
              <View style={styles.heading}>
                <Text style={styles.title}>RentMaster</Text>
                <Text style={styles.subtitle}>50 imóveis disponíveis</Text>
              </View>
              <Pressable
                accessibilityRole="button"
                accessibilityLabel="Sair da conta"
                accessibilityState={{ disabled: isLoggingOut }}
                disabled={isLoggingOut}
                onPress={handleLogout}
                style={({ pressed }) => [
                  styles.logoutButton,
                  pressed && styles.logoutPressed,
                ]}
              >
                <Ionicons name="log-out-outline" size={24} color="#ef4444" />
              </Pressable>
            </View>
            <Pressable
              accessibilityRole="button"
              accessibilityLabel="Abrir filtros"
              onPress={openFilters}
              style={({ pressed }) => [
                styles.filterButton,
                pressed && styles.logoutPressed,
              ]}
            >
              <Ionicons name="options-outline" size={20} color="#60a5fa" />
              <Text style={styles.filterButtonText}>Filtros</Text>
              {activeFiltersCount > 0 && (
                <View style={styles.filterCount}>
                  <Text style={styles.filterCountText}>{activeFiltersCount}</Text>
                </View>
              )}
            </Pressable>
          </View>
        }
        renderItem={({ item }) => <PropertyCard property={item} />}
        ListEmptyComponent={
          isLoading ? (
            <ActivityIndicator style={styles.state} size="large" color="#60a5fa" />
          ) : (
            <View style={styles.state}>
              <Text style={styles.message}>
                {errorMessage ||
                  (activeFiltersCount
                    ? 'Nenhum imóvel corresponde aos filtros selecionados.'
                    : 'Nenhum imóvel encontrado no momento.')}
              </Text>
              {errorMessage && supabase && (
                <Pressable
                  onPress={() => {
                    setIsLoading(true);
                    setErrorMessage(null);
                    void loadProperties();
                  }}
                  style={styles.retryButton}
                >
                  <Text style={styles.retryText}>Tentar novamente</Text>
                </Pressable>
              )}
            </View>
          )
        }
      />
      <Modal
        animationType="slide"
        onRequestClose={() => setIsFilterModalVisible(false)}
        transparent
        visible={isFilterModalVisible}
      >
        <View style={styles.modalRoot}>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Fechar filtros"
            onPress={() => setIsFilterModalVisible(false)}
            style={styles.modalOverlay}
          />
          <KeyboardAvoidingView behavior="padding" style={styles.modalKeyboard}>
            <View style={styles.filterSheet}>
              <View style={styles.sheetHandle} />
              <View style={styles.sheetHeader}>
                <Text style={styles.sheetTitle}>Filtrar imóveis</Text>
                <Pressable
                  accessibilityRole="button"
                  accessibilityLabel="Fechar filtros"
                  onPress={() => setIsFilterModalVisible(false)}
                  style={styles.closeButton}
                >
                  <Ionicons name="close" size={22} color="#94a3b8" />
                </Pressable>
              </View>

              <ScrollView
                keyboardShouldPersistTaps="handled"
                showsVerticalScrollIndicator={false}
                style={styles.filterScroll}
              >
                <View style={styles.filterField}>
                  <Text style={styles.filterLabel}>Bairro</Text>
                  <Pressable
                    accessibilityRole="button"
                    accessibilityLabel="Selecionar bairro"
                    accessibilityState={{ expanded: isNeighborhoodDropdownOpen }}
                    onPress={() =>
                      setIsNeighborhoodDropdownOpen((isOpen) => !isOpen)
                    }
                    style={styles.dropdownButton}
                  >
                    <Text
                      style={[
                        styles.dropdownButtonText,
                        !draftFilters.neighborhood && styles.dropdownPlaceholder,
                      ]}
                    >
                      {draftFilters.neighborhood || 'Todos os bairros'}
                    </Text>
                    <Ionicons
                      name={isNeighborhoodDropdownOpen ? 'chevron-up' : 'chevron-down'}
                      size={18}
                      color="#94a3b8"
                    />
                  </Pressable>
                  {isNeighborhoodDropdownOpen && (
                    <View style={styles.dropdownOptions}>
                      <ScrollView
                        nestedScrollEnabled
                        showsVerticalScrollIndicator={false}
                      >
                        {[
                          { label: 'Todos os bairros', value: '' },
                          ...neighborhoods.map((neighborhood) => ({
                            label: neighborhood,
                            value: neighborhood,
                          })),
                        ].map((option) => {
                          const isSelected = draftFilters.neighborhood === option.value;
                          return (
                            <Pressable
                              accessibilityRole="button"
                              accessibilityState={{ selected: isSelected }}
                              key={option.value || 'all-neighborhoods'}
                              onPress={() => {
                                updateDraftFilter('neighborhood', option.value);
                                setIsNeighborhoodDropdownOpen(false);
                              }}
                              style={[
                                styles.dropdownOption,
                                isSelected && styles.dropdownOptionSelected,
                              ]}
                            >
                              <Text
                                style={[
                                  styles.dropdownOptionText,
                                  isSelected && styles.dropdownOptionTextSelected,
                                ]}
                              >
                                {option.label}
                              </Text>
                            </Pressable>
                          );
                        })}
                      </ScrollView>
                    </View>
                  )}
                </View>
                {renderFilterInput(
                  'Preço máximo',
                  'Ex.: 2500',
                  draftFilters.maxPrice,
                  (value) => updateDraftFilter('maxPrice', value),
                  'decimal-pad'
                )}
                {renderFilterInput(
                  'Área mínima (m²)',
                  'Ex.: 60',
                  draftFilters.minArea,
                  (value) => updateDraftFilter('minArea', value),
                  'decimal-pad'
                )}

                <View style={styles.filterField}>
                  <Text style={styles.filterLabel}>Classificação</Text>
                  <View style={styles.chipRow}>
                    {(['Todos', 'Justo', 'Caro', 'Barato'] as const).map((classification) => {
                      const isSelected =
                        draftFilters.classification === classification;
                      return (
                        <Pressable
                          accessibilityRole="button"
                          accessibilityState={{ selected: isSelected }}
                          key={classification}
                          onPress={() => updateDraftFilter('classification', classification)}
                          style={[
                            styles.filterChip,
                            isSelected && styles.filterChipSelected,
                          ]}
                        >
                          <Text
                            style={[
                              styles.filterChipText,
                              isSelected && styles.filterChipTextSelected,
                            ]}
                          >
                            {classification}
                          </Text>
                        </Pressable>
                      );
                    })}
                  </View>
                </View>
              </ScrollView>

              <Pressable
                accessibilityRole="button"
                onPress={applyFilters}
                style={({ pressed }) => [
                  styles.applyButton,
                  pressed && styles.applyButtonPressed,
                ]}
              >
                <Text style={styles.applyButtonText}>Aplicar Filtros</Text>
              </Pressable>
            </View>
          </KeyboardAvoidingView>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#121418',
  },
  listContent: {
    padding: 20,
  },
  header: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  heading: {
    flex: 1,
  },
  title: {
    color: '#f8fafc',
    fontSize: 28,
    fontWeight: '700',
  },
  subtitle: {
    color: '#94a3b8',
    fontSize: 15,
    marginTop: 6,
  },
  filterButton: {
    alignItems: 'center',
    alignSelf: 'flex-start',
    backgroundColor: '#1e293b',
    borderColor: '#334155',
    borderRadius: 12,
    borderWidth: 1,
    flexDirection: 'row',
    gap: 8,
    marginBottom: 20,
    minHeight: 44,
    paddingHorizontal: 14,
  },
  filterButtonText: {
    color: '#e2e8f0',
    fontSize: 14,
    fontWeight: '600',
  },
  filterCount: {
    alignItems: 'center',
    backgroundColor: '#2563eb',
    borderRadius: 10,
    height: 20,
    justifyContent: 'center',
    minWidth: 20,
    paddingHorizontal: 5,
  },
  filterCountText: {
    color: '#ffffff',
    fontSize: 11,
    fontWeight: '700',
  },
  logoutButton: {
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 16,
    minHeight: 44,
    minWidth: 44,
  },
  logoutPressed: {
    opacity: 0.65,
  },
  separator: {
    height: 14,
  },
  state: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 36,
  },
  message: {
    color: '#cbd5e1',
    fontSize: 15,
    textAlign: 'center',
  },
  retryButton: {
    backgroundColor: '#2563eb',
    borderRadius: 10,
    marginTop: 16,
    paddingHorizontal: 18,
    paddingVertical: 10,
  },
  retryText: {
    color: '#ffffff',
    fontWeight: '600',
  },
  modalRoot: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  modalOverlay: {
    backgroundColor: 'rgba(0, 0, 0, 0.65)',
    bottom: 0,
    left: 0,
    position: 'absolute',
    right: 0,
    top: 0,
  },
  modalKeyboard: {
    justifyContent: 'flex-end',
  },
  filterSheet: {
    backgroundColor: '#1a1f2b',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    maxHeight: '85%',
    paddingBottom: 28,
    paddingHorizontal: 20,
    paddingTop: 12,
  },
  sheetHandle: {
    alignSelf: 'center',
    backgroundColor: '#475569',
    borderRadius: 3,
    height: 5,
    marginBottom: 16,
    width: 40,
  },
  sheetHeader: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  sheetTitle: {
    color: '#f8fafc',
    fontSize: 20,
    fontWeight: '700',
  },
  closeButton: {
    alignItems: 'center',
    height: 36,
    justifyContent: 'center',
    width: 36,
  },
  filterScroll: {
    flexShrink: 1,
  },
  filterField: {
    marginBottom: 18,
  },
  filterLabel: {
    color: '#cbd5e1',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
  },
  filterInput: {
    backgroundColor: '#0f172a',
    borderColor: '#334155',
    borderRadius: 12,
    borderWidth: 1,
    color: '#f8fafc',
    fontSize: 15,
    minHeight: 48,
    paddingHorizontal: 14,
  },
  dropdownButton: {
    alignItems: 'center',
    backgroundColor: '#0f172a',
    borderColor: '#334155',
    borderRadius: 12,
    borderWidth: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    minHeight: 48,
    paddingHorizontal: 14,
  },
  dropdownButtonText: {
    color: '#f8fafc',
    flex: 1,
    fontSize: 15,
    marginRight: 12,
  },
  dropdownPlaceholder: {
    color: '#64748b',
  },
  dropdownOptions: {
    backgroundColor: '#0f172a',
    borderColor: '#334155',
    borderRadius: 12,
    borderWidth: 1,
    marginTop: 6,
    maxHeight: 180,
    overflow: 'hidden',
  },
  dropdownOption: {
    minHeight: 42,
    justifyContent: 'center',
    paddingHorizontal: 14,
  },
  dropdownOptionSelected: {
    backgroundColor: '#1e3a8a',
  },
  dropdownOptionText: {
    color: '#cbd5e1',
    fontSize: 14,
  },
  dropdownOptionTextSelected: {
    color: '#ffffff',
    fontWeight: '700',
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  filterChip: {
    backgroundColor: '#0f172a',
    borderColor: '#334155',
    borderRadius: 20,
    borderWidth: 1,
    paddingHorizontal: 14,
    paddingVertical: 9,
  },
  filterChipSelected: {
    backgroundColor: '#1d4ed8',
    borderColor: '#3b82f6',
  },
  filterChipText: {
    color: '#cbd5e1',
    fontSize: 13,
    fontWeight: '500',
  },
  filterChipTextSelected: {
    color: '#ffffff',
    fontWeight: '700',
  },
  applyButton: {
    alignItems: 'center',
    backgroundColor: '#2563eb',
    borderRadius: 12,
    justifyContent: 'center',
    marginTop: 8,
    minHeight: 52,
  },
  applyButtonPressed: {
    backgroundColor: '#1d4ed8',
  },
  applyButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
  },
});
