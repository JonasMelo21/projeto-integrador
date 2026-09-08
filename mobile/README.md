# Mobile - RentMaster App (Flutter)

Aplicativo nativo para **iOS** e **Android** que permite aos usuários:
- Fazer login seguro com Google
- Navegar lista de imóveis disponíveis
- Ver classificação de preço (Barato/Justo/Caro)
- Favoritar imóveis
- Visualizar mapa de localização
- Ver detalhes completos do imóvel

Built com **Flutter** para máxima performance e reuso de código entre plataformas.

---

## 🏗️ Arquitetura Mobile

```
UI Layer (Flutter Widgets)
    ├── LoginPage (Google OAuth)
    ├── HomePage (Lista de imóveis)
    ├── PropertyDetailsPage (Detalhes)
    ├── MapPage (Geolocalização)
    ├── FavoritesPage (Favoritos)
    └── ProfilePage (Perfil do usuário)
          ↓
Business Logic (State Management)
    ├── Controllers
    └── Repositories
          ↓
Data Layer (API Client)
    ├── HTTP requests
    ├── JWT token management
    └── Local storage (SharedPreferences)
          ↓
Backend API (FastAPI)
    http://localhost:8000
```

---

## 📁 Estrutura de Arquivos

```
mobile/
├── lib/
│   ├── main.dart                  # Entry point
│   ├── config/
│   │   └── api_client.dart        # HTTP client + API calls
│   ├── screens/
│   │   ├── login_page.dart        # Login com Google
│   │   ├── sobre_page.dart        # Sobre/Perfil
│   │   └── ... (outras telas)
│   ├── models/
│   │   └── ... (modelos de dados)
│   └── widgets/
│       └── ... (componentes reutilizáveis)
├── pubspec.yaml                  # Dependências Dart/Flutter
├── pubspec.lock                  # Lock file
└── README.md                      # Este arquivo
```

---

## 🔑 Arquivos Principais

### `main.dart`
Entry point do aplicativo:
- Inicializa Flutter
- Configura tema (cores, fontes, estilos)
- Define rotas entre telas
- Seta home screen (LoginPage ou HomePage)

### `config/api_client.dart`
Cliente HTTP centralizado:

**Funções principais:**
- `login(idToken)` → POST /auth/google
- `fetchImoveis(skip, limit)` → GET /api/imoveis
- `fetchImovel(id)` → GET /api/imoveis/{id}
- `fetchDimensoes()` → GET /api/dimensoes

**Responsabilidades:**
- Gerenciar sessionToken (armazenar/recuperar)
- Adicionar headers de autenticação automaticamente
- Tratar erros HTTP (401, 404, 500)
- Refresh token quando expirado

```dart
// Exemplo de uso:
final imoveis = await apiClient.fetchImoveis(skip: 0, limit: 10);
// Automaticamente inclui: Authorization: Bearer {sessionToken}
```

### `screens/login_page.dart`
Tela de autenticação:

**Fluxo:**
1. Usuário tapa "Continuar com Google"
2. Plugin Google Sign-In abre diálogo nativo
3. Usuário autentica com Google
4. Retorna `idToken`
5. Frontend POST /auth/google com idToken
6. Backend valida e retorna `sessionToken`
7. Frontend armazena sessionToken em SharedPreferences
8. Navega para HomePage

**Features:**
- Tratamento de erros (rede, autenticação)
- Loading state (spinner)
- Botão desabilitado durante requisição

### `screens/home_page.dart`
Listagem de imóveis:

**Componentes:**
- ListView com paginação (lazy loading)
- PropertyCard para cada imóvel
- Exibe: título, preço, área, classificação ML
- Botão "Favoritar"
- Filtro por bairro (se implementado)

### `screens/property_details_page.dart`
Detalhes completo do imóvel:

**Exibições:**
- Galeria de imagens (carousel)
- Informações principais (quartos, banheiros, vagas)
- Descrição completa
- Localização no mapa
- Dados da imobiliária
- Classificação de preço (Barato/Justo/Caro)

### `screens/map_page.dart`
Visualização geográfica:

**Features:**
- Mapa com pins dos imóveis
- Clustering automático
- Filtro por bairro/preço
- Tapa no pin para ver detalhes

---

## 📊 Fluxo de Autenticação

```
1. App inicia
   ↓
2. Verifica sessionToken em SharedPreferences
   ├─ Se existe + válido → Vai para HomePage
   └─ Se não → Mostra LoginPage
   ↓
3. Usuário clica "Continuar com Google"
   ↓
4. Google Sign-In plugin (iOS/Android nativo)
   ├─ Abre diálogo de login
   ├─ Usuário autentica
   └─ Retorna idToken
   ↓
5. Frontend POST /auth/google { idToken }
   ↓
6. Backend retorna sessionToken
   ↓
7. Frontend armazena em SharedPreferences
   ↓
8. Navega para HomePage ✅
```

---

## 🌐 API Calls (ApiClient)

### Login
```dart
POST /auth/google
Body: { "idToken": "..." }
Response: { "sessionToken": "...", "email": "...", "nome": "..." }
```

### Listar Imóveis
```dart
GET /api/imoveis?skip=0&limit=10
Headers: Authorization: Bearer {sessionToken}
Response: [
  {
    "id_imovel": 1,
    "titulo": "Apt 2 quartos",
    "preco": 2500,
    "area_m2": 75,
    "classificacao_preco": "Preço Justo"
  }
]
```

### Detalhes de Imóvel
```dart
GET /api/imoveis/1
Headers: Authorization: Bearer {sessionToken}
Response: {
  "id_imovel": 1,
  "titulo": "...",
  "preco": 2500,
  "quartos": 2,
  "banheiros": 1,
  "vagas": 1,
  "area_m2": 75,
  "descricao": "Imóvel bem localizado...",
  "imagem": "https://...",
  "imobiliaria": { "nome": "...", "telefone": "..." },
  "classificacao_preco": "Preço Justo"
}
```

---

## 🚀 Como Rodar

### Pré-requisitos

- **Flutter SDK**: [Instalar](https://flutter.dev/docs/get-started/install)
- **Android Studio** ou **Xcode** (para emulador)
- **Backend rodando**: `docker compose up -d backend`

### Opção 1: Google Project IDX (Recomendado - Cloud)

```bash
# 1. Abrir em https://idx.google.com
# 2. Importar este repositório
# 3. Selecionar "Flutter" como template
# 4. IDE pronta com Flutter SDK + emulador
# 5. Clicar "Run"
```

Vantagem: Sem dependências locais, tudo na nuvem.

### Opção 2: Local com Android Studio

```bash
# 1. Instalar Flutter SDK
flutter --version

# 2. Instalar dependências
cd mobile
flutter pub get

# 3. Iniciar emulador Android
# (abrir Android Studio → AVD Manager → iniciar emulador)

# 4. Rodar app
flutter run

# 5. App abre em emulador
```

### Opção 3: Local com Xcode (iOS)

```bash
cd mobile
flutter pub get
flutter run -d macos
```

### Opção 4: Docker (Compilação)

```bash
# Build APK
docker run --rm -v ${PWD}/mobile:/app -w /app ghcr.io/cirruslabs/flutter:latest flutter build apk

# APK estará em: mobile/build/app/outputs/flutter-apk/app-release.apk
```

---

## 🧪 Como Testar

### Teste de Login
1. Abra app
2. Clique "Continuar com Google"
3. Faça login com sua conta Google
4. Se OK → Navega para HomePage ✅

### Teste de Listagem
1. Na HomePage, role para baixo
2. Deve carregar lista de imóveis
3. Cada card exibe: título, preço, área, classificação

### Teste de Detalhes
1. Tapa em um imóvel
2. Abre PropertyDetailsPage
3. Exibe todas as informações

### Teste Offline
1. Desative internet (ou use `flutter run --verbose`)
2. App deve exibir mensagem de erro
3. Verificar error handling

---

## 📊 Dependências

Veja `mobile/pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  google_sign_in: ^6.1.0          # Google OAuth
  http: ^1.1.0                    # HTTP client
  provider: ^6.0.0                # State management
  shared_preferences: ^2.2.0      # Local storage
  google_maps_flutter: ^2.5.0     # Maps
  image_picker: ^1.0.0            # Galeria de fotos
  intl: ^0.19.0                   # Internacionalização
```

---

## 🔐 Segurança

### ✅ Implementado
- Google OAuth 2.0 nativo (iOS/Android)
- Armazenamento seguro de token (Keychain/Keystore)
- HTTPS para todas as requisições
- Token refresh automático

### 🔜 Roadmap
- [ ] Biometric unlock (Face ID / Fingerprint)
- [ ] Certificate pinning
- [ ] Rate limiting local

---

## 🎨 UI/UX Components

### LoginPage
- Google Sign-In button (estilo material)
- Splash screen com logo
- Error messages amigáveis

### HomePage
- Bottom navigation (5 abas)
- PropertyCard com imagem/preço/classificação
- Pull-to-refresh
- Loading skeleton

### PropertyDetailsPage
- Carousel de imagens
- Expandable description
- Favorite button
- Share button
- Call imobiliária

### MapPage
- Google Maps integrado
- Pins dos imóveis
- Filtro lateral
- Tap → vai para detalhes

---

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| "flutter: command not found" | Adicionar Flutter ao PATH ou usar Docker |
| Emulador não inicia | Abrir Android Studio → AVD Manager |
| Google Sign-In falha | Verificar Client ID em `google_sign_in` config |
| Backend conexão recusada | Verificar IP: usar `10.0.2.2` em Android emulator |
| Imagens não carregam | Verificar URLs em backend e permissões INTERNET |

---

## 🔄 Arquitetura da Navegação

```
LoginPage
    ↓ (após autenticação)
HomePage (aba selecionada por padrão)
    ├─ Aba 1: Home (lista de imóveis)
    ├─ Aba 2: Map (mapa)
    ├─ Aba 3: Search (busca)
    ├─ Aba 4: Favorites (favoritos)
    └─ Aba 5: Profile (perfil)
         ↓
PropertyDetailsPage (tapa em um imóvel)
    ├─ Back button → volta para HomePage
    └─ Share/Favorite → ações
```

---

## 📚 Referências

- [Flutter Docs](https://flutter.dev/docs)
- [Google Sign-In for Flutter](https://pub.dev/packages/google_sign_in)
- [Provider State Management](https://pub.dev/packages/provider)
- [Google Maps Flutter](https://pub.dev/packages/google_maps_flutter)

---

## 🎯 Próximos Passos

1. Instalar Flutter SDK localmente
2. Rodar `flutter pub get` na pasta mobile
3. Iniciar emulador ou usar Project IDX
4. Testar fluxo completo de login
5. Testar listagem de imóveis

---

**Status**: ✅ Beta com autenticação Google funcional

**Última Atualização**: Setembro 2026
