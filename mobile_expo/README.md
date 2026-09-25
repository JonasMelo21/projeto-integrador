# Mobile Expo — RentMaster

App mobile Expo (React Native) que conecta usuários ao backend para analisar preços de aluguel em tempo real.

## 🎯 Objetivo

Interface mobile nativa para iOS/Android com:
- Login via Google OAuth
- Listagem de imóveis com classificação ML
- Busca e filtros por bairro/preço/tamanho
- Interface responsiva e performática

## 📁 Estrutura

```
src/
├── screens/          # Telas principais
├── components/       # Componentes reutilizáveis
├── config/          # Configurações
│   └── api_client.ts # Cliente HTTP para backend
├── models/          # Tipos TypeScript e interfaces
├── hooks/           # Custom hooks (tema, cores, etc)
├── lib/             # Integrações externas
│   └── supabase.ts  # Cliente Supabase
└── constants/       # Constantes (paleta de cores, etc)
```

## 🚀 Setup Rápido

```bash
# Instalar dependências
npm install

# Desenvolvimento local
npm run web         # Usar Expo Go web
npx expo start      # Escanear QR code no Expo Go (iOS/Android)

# Build para produção
npm run build:ios
npm run build:android
```

## 🔑 Arquivos Principais

| Arquivo | Função |
|---------|--------|
| `config/api_client.ts` | Cliente HTTP (chamadas ao backend) |
| `lib/supabase.ts` | Autenticação e dados (Supabase) |
| `hooks/use-theme.ts` | Provider de tema (claro/escuro) |
| `hooks/use-color-scheme.ts` | Detecção de esquema de cores |
| `constants/theme.ts` | Paleta de cores e estilos |

## 🔐 Autenticação

```typescript
// Fluxo OAuth
1. Usuário toca "Continuar com Google"
2. Google Sign-In abre dialog nativo
3. Backend valida token JWT
4. Retorna sessionToken
5. Store local salva token
6. Requisições futuras incluem: Authorization: Bearer {token}
```

## 📡 Integrações

| Serviço | Função |
|---------|--------|
| **Google OAuth** | Autenticação nativa |
| **Backend FastAPI** | API de imóveis + ML inference |
| **Supabase** | Autenticação alternativa e realtime |

## 🎨 Temas e Cores

O app suporta modo claro/escuro automático:
- Detecta preferência do sistema com `use-color-scheme`
- Aplica tema via `useTheme()` hook
- Cores definidas em `constants/theme.ts`

## 🔧 O que Contribuir

| Tarefa | Arquivo |
|--------|---------|
| Adicionar tela | `src/screens/` |
| Novo componente | `src/components/` |
| Chamada API | `config/api_client.ts` |
| Ajustar tema | `constants/theme.ts` |
| Custom hook | `src/hooks/` |

## 🚨 Pontos Importantes

- 📱 **Expo Web**: Não suporta Google Sign-In nativo (usar Supabase em web)
- 🔑 **Token na memória**: sessionToken perdido ao fechar app (melhoria futura: async storage)
- 🎨 **Theme provider**: Sempre envolver app com `ThemeProvider`
- 📡 **CORS**: Backend deve permitir requisições do mobile

## 📚 Documentação Expo

Para updates e features, consulte versão exata em `AGENTS.md`:
```
https://docs.expo.dev/versions/vXX.X.X/
```

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| "Cannot find module" | `npm install` |
| OAuth não funciona em web | Usar Supabase Auth em web |
| Theme não aplicando | Verificar `ThemeProvider` no root |
| API retorna CORS error | Adicionar origem mobile no backend |
