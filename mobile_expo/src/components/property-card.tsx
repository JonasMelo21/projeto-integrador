import { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Image,
  Linking,
  Pressable,
  Share,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import { supabase } from '../lib/supabase';

type Property = {
  id_imovel?: string | number | null;
  id?: string | number | null;
  titulo?: string | null;
  preco?: number | string | null;
  valor_aluguel?: number | string | null;
  bairro?: string | null;
  local_bairro?: string | null;
  url?: string | null;
  imagem?: string | null;
  ml_label?: string | null;
  classificacao_preco?: string | null;
};

type PropertyCardProps = {
  property: Property;
};

function formatPrice(price: number | string) {
  if (typeof price === 'number') {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(price);
  }

  return price;
}

export default function PropertyCard({ property }: PropertyCardProps) {
  const [isFavorito, setIsFavorito] = useState(false);
  const [isLoadingFavorite, setIsLoadingFavorite] = useState(true);
  const [isUpdatingFavorite, setIsUpdatingFavorite] = useState(false);
  const { url } = property;
  const rawPropertyId = property.id_imovel ?? property.id;
  const propertyId = rawPropertyId == null ? '' : String(rawPropertyId);
  const title =
    property.titulo || (property.bairro || property.local_bairro
      ? `Imóvel em ${property.bairro || property.local_bairro}`
      : 'Imóvel para alugar');
  const price = property.preco ?? property.valor_aluguel ?? 'Preço sob consulta';
  const rawClassification = property.ml_label ?? property.classificacao_preco;
  const normalizedClassification = rawClassification
    ?.trim()
    .toLocaleLowerCase('pt-BR')
    .replace(/^preço\s+/, '');
  const classification =
    normalizedClassification === 'barato'
      ? 'Barato'
      : normalizedClassification === 'justo'
        ? 'Justo'
        : normalizedClassification === 'caro'
          ? 'Caro'
          : null;
  const badgeColor =
    classification === 'Barato'
      ? '#16a34a'
      : classification === 'Caro'
        ? '#dc2626'
        : '#2563eb';

  async function trackInteraction(
    interactionType: 'clique' | 'compartilhamento' | 'favorito',
    userId?: string
  ) {
    const client = supabase;
    if (!client || rawPropertyId == null) {
      return;
    }

    try {
      let interactionUserId = userId;
      if (!interactionUserId) {
        const { data: userData, error: userError } = await client.auth.getUser();
        if (userError) {
          throw userError;
        }
        interactionUserId = userData.user?.id;
      }

      if (!interactionUserId) {
        return;
      }

      const { error } = await client.from('interacoes_app').insert({
        imovel_id: propertyId,
        user_id: interactionUserId,
        tipo_interacao: interactionType,
        created_at: new Date().toISOString(),
      });

      if (error) {
        throw error;
      }
    } catch (error) {
      console.error(`Erro ao registrar interação (${interactionType}):`, error);
    }
  }

  function handlePress() {
    if (!url) {
      return;
    }

    void trackInteraction('clique');
    Linking.openURL(url).catch((err) => console.error('Erro ao abrir URL:', err));
  }

  useEffect(() => {
    let isMounted = true;

    async function loadFavorite() {
      if (!propertyId) {
        setIsLoadingFavorite(false);
        return;
      }

      const client = supabase;
      if (!client) {
        setIsLoadingFavorite(false);
        return;
      }

      try {
        const { data: userData, error: userError } = await client.auth.getUser();
        if (userError) {
          throw userError;
        }

        if (!userData.user) {
          return;
        }

        const { data, error } = await client
          .from('favoritos')
          .select('imovel_id')
          .eq('imovel_id', propertyId)
          .eq('user_id', userData.user.id)
          .maybeSingle();

        if (error) {
          throw error;
        }

        if (isMounted) {
          setIsFavorito(Boolean(data));
        }
      } catch (error) {
        console.error('Erro ao consultar favorito:', error);
        if (isMounted) {
          Alert.alert('Não foi possível carregar', 'Tente verificar seus favoritos novamente.');
        }
      } finally {
        if (isMounted) {
          setIsLoadingFavorite(false);
        }
      }
    }

    void loadFavorite();

    return () => {
      isMounted = false;
    };
  }, [propertyId]);

  async function toggleFavorito() {
    if (isUpdatingFavorite) {
      return;
    }

    if (!propertyId) {
      Alert.alert('Favorito indisponível', 'Este imóvel não possui um identificador válido.');
      return;
    }

    const client = supabase;
    if (!client) {
      Alert.alert(
        'Favoritos indisponíveis',
        'As variáveis do Supabase não foram configuradas neste build.'
      );
      return;
    }

    setIsUpdatingFavorite(true);

    try {
      const { data: userData, error: userError } = await client.auth.getUser();
      if (userError) {
        throw userError;
      }

      const user = userData.user;
      if (!user) {
        Alert.alert('Entre na sua conta', 'Faça login para salvar imóveis como favoritos.');
        return;
      }

      if (isFavorito) {
        const { error } = await client
          .from('favoritos')
          .delete()
          .eq('imovel_id', propertyId)
          .eq('user_id', user.id);

        if (error) {
          throw error;
        }

        setIsFavorito(false);
      } else {
        const { error } = await client.from('favoritos').insert({
          imovel_id: propertyId,
          user_id: user.id,
        });

        if (error) {
          throw error;
        }

        setIsFavorito(true);
        void trackInteraction('favorito', user.id);
      }
    } catch (error) {
      console.error('Erro ao atualizar favorito:', error);
      Alert.alert('Não foi possível atualizar', 'Tente favoritar o imóvel novamente.');
    } finally {
      setIsUpdatingFavorite(false);
    }
  }

  async function shareProperty() {
    const formattedPrice = formatPrice(price);
    const propertyReference = url || `ID do imóvel: ${propertyId}`;

    try {
      const result = await Share.share({
        message: `Confira este imóvel no RentMaster!\n${title}\nPreço: ${formattedPrice}\n${propertyReference}`,
      });

      if (result.action === Share.sharedAction) {
        void trackInteraction('compartilhamento');
      }
    } catch (error) {
      console.error('Erro ao compartilhar imóvel:', error);
      Alert.alert('Não foi possível compartilhar', 'Tente novamente.');
    }
  }

  return (
    <View style={styles.card}>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel={`Abrir anúncio: ${title}`}
        disabled={!url}
        onPress={handlePress}
      >
        <View style={styles.imageContainer}>
          {property.imagem ? (
            <Image
              accessibilityLabel={`Foto de ${title}`}
              resizeMode="cover"
              source={{ uri: property.imagem }}
              style={styles.image}
            />
          ) : (
            <View style={styles.imagePlaceholder}>
              <Ionicons name="image-outline" size={36} color="#64748b" />
            </View>
          )}
          {classification && (
            <View style={[styles.badge, { backgroundColor: badgeColor }]}>
              <Text style={styles.badgeText}>{classification}</Text>
            </View>
          )}
        </View>

        <View style={styles.information}>
          <Text style={styles.title}>{title}</Text>
          <Text style={styles.price}>{formatPrice(price)}</Text>
          {(property.bairro || property.local_bairro) && (
            <Text style={styles.reference}>{property.bairro || property.local_bairro}</Text>
          )}
          {propertyId && <Text style={styles.reference}>Imóvel #{propertyId}</Text>}
        </View>
      </Pressable>

      <View style={styles.footer}>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Compartilhar imóvel"
          onPress={shareProperty}
          style={({ pressed }) => [styles.actionButton, pressed && styles.actionPressed]}
        >
          <Ionicons name="share-social-outline" size={20} color="#60a5fa" />
          <Text style={styles.actionText}>Compartilhar</Text>
        </Pressable>

        <Pressable
          accessibilityRole="button"
          accessibilityLabel={isFavorito ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}
          accessibilityState={{ disabled: isLoadingFavorite || isUpdatingFavorite }}
          disabled={isLoadingFavorite || isUpdatingFavorite}
          onPress={toggleFavorito}
          style={({ pressed }) => [styles.actionButton, pressed && styles.actionPressed]}
        >
          {isLoadingFavorite || isUpdatingFavorite ? (
            <ActivityIndicator size="small" color="#f87171" />
          ) : (
            <Ionicons
              name={isFavorito ? 'heart' : 'heart-outline'}
              size={21}
              color={isFavorito ? '#ef4444' : '#f87171'}
            />
          )}
          <Text style={styles.actionText}>
            {isFavorito ? 'Favoritado' : 'Favoritar'}
          </Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#1e293b',
    borderColor: '#334155',
    borderRadius: 16,
    borderWidth: 1,
    overflow: 'hidden',
  },
  imageContainer: {
    height: 190,
    position: 'relative',
    width: '100%',
  },
  image: {
    height: '100%',
    width: '100%',
  },
  imagePlaceholder: {
    alignItems: 'center',
    backgroundColor: '#334155',
    height: '100%',
    justifyContent: 'center',
    width: '100%',
  },
  badge: {
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 6,
    position: 'absolute',
    right: 12,
    top: 12,
  },
  badgeText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '700',
  },
  information: {
    gap: 6,
    padding: 18,
  },
  title: {
    color: '#f8fafc',
    fontSize: 18,
    fontWeight: '700',
  },
  price: {
    color: '#60a5fa',
    fontSize: 17,
    fontWeight: '700',
  },
  reference: {
    color: '#94a3b8',
    fontSize: 12,
  },
  footer: {
    borderTopColor: '#334155',
    borderTopWidth: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginHorizontal: 18,
    marginTop: 0,
    paddingTop: 12,
    paddingBottom: 14,
  },
  actionButton: {
    alignItems: 'center',
    flexDirection: 'row',
    gap: 8,
    minHeight: 40,
    paddingHorizontal: 8,
  },
  actionPressed: {
    opacity: 0.7,
  },
  actionText: {
    color: '#e2e8f0',
    fontSize: 13,
    fontWeight: '600',
  },
});
