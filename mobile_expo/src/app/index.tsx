import { useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as WebBrowser from 'expo-web-browser';
import * as Linking from 'expo-linking';
import { router } from 'expo-router';

import { supabase } from '@/lib/supabase';

WebBrowser.maybeCompleteAuthSession();

export default function LoginScreen() {
  const [isSigningIn, setIsSigningIn] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleGoogleSignIn() {
    console.log('>>> [LOG] Botão de Login clicado!');
    setIsSigningIn(true);
    setErrorMessage(null);

    try {
      const redirectUrl = Linking.createURL('/');
      console.log('>>> [LOG] URL de Retorno gerada:', redirectUrl);

      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: redirectUrl,
          skipBrowserRedirect: true,
        },
      });

      if (error) {
        console.log('>>> [ERRO SUPABASE]:', error.message);
        setErrorMessage(error.message);
      } else if (data?.url) {
        console.log('>>> [SUCESSO]: Abrindo o navegador...');

        const result = await WebBrowser.openAuthSessionAsync(data.url, redirectUrl);
        console.log('>>> [RESULTADO LOGIN]:', result);

        if (result.type === 'success' && result.url) {
          // Extraindo o token de acesso (que vem escondido após o # na URL)
          const hashString = result.url.split('#')[1] || result.url.split('?')[1];

          if (hashString) {
            // Converte os parâmetros da URL em um objeto
            const params = hashString.split('&').reduce(
              (acc, param) => {
                const [key, value] = param.split('=');
                acc[key] = value;
                return acc;
              },
              {} as Record<string, string>
            );

            if (params.access_token && params.refresh_token) {
              // Registra a sessão ativamente no Supabase
              const { data: sessionData, error: sessionError } = await supabase.auth.setSession({
                access_token: params.access_token,
                refresh_token: params.refresh_token,
              });

              if (sessionError) {
                console.log('>>> [ERRO DE SESSÃO]:', sessionError);
                setErrorMessage('Falha ao registrar sessão.');
              } else {
                console.log('>>> [USUÁRIO LOGADO COM SUCESSO!]:', sessionData);
                router.replace('/explore');
              }
            } else {
              setErrorMessage('Token não encontrado na URL.');
            }
          }
        }
      }
    } catch (err: any) {
      console.log('>>> [ERRO CATASTRÓFICO]:', err);
      // Agora o erro real vai aparecer na tela em vez de "erro inesperado"
      setErrorMessage(err.message || 'Erro durante o fluxo de login.');
    } finally {
      setIsSigningIn(false);
    }
  }

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.brandMark}>
          <Text style={styles.brandMarkText}>R</Text>
        </View>

        <View style={styles.content}>
          <Text style={styles.eyebrow}>RENT MASTER</Text>
          <Text style={styles.title}>Seu proximo lar{`\n`}comeca aqui.</Text>
          <Text style={styles.subtitle}>
            Encontre, compare e gerencie seus imoveis em um so lugar.
          </Text>

          <View style={styles.accentLine} />

          <Pressable
            disabled={isSigningIn}
            onPress={handleGoogleSignIn}
            style={({ pressed }) => [styles.googleButton, pressed && styles.googleButtonPressed]}
          >
            {isSigningIn ? (
              <ActivityIndicator color="#ffffff" />
            ) : (
              <>
                <View style={styles.googleIcon}>
                  <Text style={styles.googleIconText}>G</Text>
                </View>
                <Text style={styles.googleButtonText}>Entrar com Google</Text>
              </>
            )}
          </Pressable>

          {errorMessage && <Text style={styles.errorMessage}>{errorMessage}</Text>}
        </View>

        <Text style={styles.footer}>Acesso seguro para sua jornada imobiliaria</Text>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121418',
  },
  safeArea: {
    flex: 1,
    paddingHorizontal: 28,
    paddingVertical: 24,
    justifyContent: 'space-between',
    alignItems: 'center',
    width: '100%',
    maxWidth: 560,
    alignSelf: 'center',
  },
  brandMark: {
    alignItems: 'center',
    justifyContent: 'center',
    width: 52,
    height: 52,
    borderRadius: 16,
    backgroundColor: '#2563eb',
    alignSelf: 'flex-start',
  },
  brandMarkText: {
    color: '#ffffff',
    fontSize: 28,
    fontWeight: '800',
  },
  content: {
    width: '100%',
    alignItems: 'center',
    marginTop: -20,
  },
  eyebrow: {
    color: '#60a5fa',
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 3,
    marginBottom: 18,
  },
  title: {
    color: '#f8fafc',
    fontSize: 42,
    fontWeight: '700',
    letterSpacing: 0,
    textAlign: 'center',
    lineHeight: 47,
  },
  subtitle: {
    color: '#94a3b8',
    fontSize: 16,
    lineHeight: 24,
    marginTop: 20,
    maxWidth: 330,
    textAlign: 'center',
  },
  accentLine: {
    width: 44,
    height: 3,
    backgroundColor: '#2563eb',
    marginVertical: 34,
  },
  googleButton: {
    width: '100%',
    minHeight: 60,
    borderRadius: 16,
    backgroundColor: '#1e293b',
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
    gap: 12,
    borderWidth: 1,
    borderColor: '#334155',
  },
  googleButtonPressed: {
    opacity: 0.7,
    transform: [{ scale: 0.98 }],
  },
  googleIcon: {
    width: 25,
    height: 25,
    alignItems: 'center',
    justifyContent: 'center',
  },
  googleIconText: {
    color: '#60a5fa',
    fontSize: 21,
    fontWeight: '800',
  },
  googleButtonText: {
    color: '#f8fafc',
    fontSize: 16,
    fontWeight: '700',
  },
  errorMessage: {
    color: '#ef4444',
    fontSize: 13,
    marginTop: 14,
    textAlign: 'center',
  },
  footer: {
    color: '#64748b',
    fontSize: 12,
    letterSpacing: 0.3,
  },
});
