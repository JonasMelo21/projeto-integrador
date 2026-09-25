import { Image } from 'expo-image';
import * as Linking from 'expo-linking';
import { Pressable, StyleSheet, View } from 'react-native';

import { ThemedText } from './themed-text';
import { ThemedView } from './themed-view';

import { Spacing } from '@/constants/theme';
import { useTheme } from '@/hooks/use-theme';

export type PropertyCardProps = {
  id_imovel: string;
  titulo: string;
  preco: number;
  bairro: string;
  quartos?: number | null;
  vagas?: number | null;
  area?: number | null;
  imagem?: string | null;
  url: string;
  ml_label: 'Barato' | 'Justo' | 'Caro';
  onPress?: () => void;
};

export function PropertyCard({
  id_imovel,
  titulo,
  preco,
  bairro,
  quartos,
  vagas,
  area,
  imagem,
  url,
  ml_label,
  onPress,
}: PropertyCardProps) {
  const theme = useTheme();

  const handlePress = async () => {
    if (onPress) {
      onPress();
    }
    try {
      // Validar e construir URL completa se necessário
      let fullUrl = url;
      if (!fullUrl.startsWith('http')) {
        // Se for um path relativo, adicionar o domínio base
        fullUrl = `https://www.dfimoveis.com.br${fullUrl}`;
      }

      // Validar se a URL é válida
      new URL(fullUrl); // Isso vai lançar erro se a URL for inválida

      await Linking.openURL(fullUrl);
    } catch (error) {
      console.error('Erro ao abrir URL:', error);
    }
  };

  const formatPrice = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const getBadgeColors = (label: string) => {
    switch (label) {
      case 'Barato':
        return {
          backgroundColor: '#10b981', // green
          textColor: '#ffffff',
        };
      case 'Justo':
        return {
          backgroundColor: '#f59e0b', // amber
          textColor: '#1f2937',
        };
      case 'Caro':
        return {
          backgroundColor: '#ef4444', // red
          textColor: '#ffffff',
        };
      default:
        return {
          backgroundColor: '#6b7280', // gray
          textColor: '#ffffff',
        };
    }
  };

  const badgeColors = getBadgeColors(ml_label);

  const characteristics = [];
  if (quartos) characteristics.push(`${quartos} Quartos`);
  if (vagas) characteristics.push(`${vagas} Vagas`);
  if (area) characteristics.push(`${area}m²`);
  const characteristicsText = characteristics.join(' | ');

  return (
    <Pressable onPress={handlePress} style={{ flex: 1 }}>
      <ThemedView type="backgroundSelected" style={styles.card}>
        {/* Image Container */}
        <View style={styles.imageContainer}>
          <Image
            source={{ uri: imagem || '' }}
            placeholder="#e5e7eb"
            style={styles.image}
            contentFit="cover"
          />

          {/* Badge Overlay */}
          <View
            style={[
              styles.badgeContainer,
              {
                backgroundColor: badgeColors.backgroundColor,
              },
            ]}
          >
            <ThemedText
              type="smallBold"
              style={{
                color: badgeColors.textColor,
              }}
            >
              {ml_label}
            </ThemedText>
          </View>
        </View>

        {/* Content Container */}
        <View style={styles.contentContainer}>
          {/* Price */}
          <ThemedText type="title" style={styles.price}>
            {formatPrice(preco)}
          </ThemedText>

          {/* Location */}
          <ThemedText type="small" themeColor="textSecondary" style={styles.bairro}>
            {bairro}
          </ThemedText>

          {/* Title */}
          <ThemedText type="default" style={styles.titulo} numberOfLines={2}>
            {titulo}
          </ThemedText>

          {/* Characteristics */}
          {characteristicsText && (
            <ThemedText type="small" themeColor="textSecondary" style={styles.characteristics}>
              {characteristicsText}
            </ThemedText>
          )}

          {/* Property ID (for debugging/reference) */}
          <ThemedText type="small" themeColor="textSecondary" style={styles.propertyId}>
            ID: {id_imovel.substring(0, 8)}...
          </ThemedText>
        </View>
      </ThemedView>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 12,
    overflow: 'hidden',
    marginBottom: Spacing.two,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.15,
    shadowRadius: 3.84,
  },
  imageContainer: {
    position: 'relative',
    width: '100%',
    height: 200,
  },
  image: {
    width: '100%',
    height: '100%',
    backgroundColor: '#e5e7eb',
  },
  badgeContainer: {
    position: 'absolute',
    top: Spacing.two,
    right: Spacing.two,
    paddingHorizontal: Spacing.two,
    paddingVertical: Spacing.half,
    borderRadius: 6,
  },
  contentContainer: {
    padding: Spacing.two,
  },
  price: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: Spacing.half,
  },
  bairro: {
    marginBottom: Spacing.one,
  },
  titulo: {
    marginBottom: Spacing.two,
    fontWeight: '500',
  },
  characteristics: {
    marginBottom: Spacing.one,
    fontStyle: 'italic',
  },
  propertyId: {
    marginTop: Spacing.one,
    opacity: 0.6,
  },
});
