# Frontend - RentMaster (React)

Interface web moderna construída em **React** com **Vite** como build tool. Permite visualizar imóveis, análises de preço e integrações com a API backend.

---

## 🏗️ Arquitetura Frontend

```
React Components
    ├── Pages
    │   ├── LoginPage (Google OAuth)
    │   ├── HomePage (Dashboard)
    │   ├── PropertyListPage (Listagem)
    │   ├── PropertyDetailsPage (Detalhes)
    │   ├── MapPage (Mapa)
    │   ├── FavoritesPage (Favoritos)
    │   └── ProfilePage (Perfil)
    ├── Components (Reutilizáveis)
    │   ├── PropertyCard
    │   ├── PropertyFilter
    │   ├── Header
    │   └── Footer
    └── Hooks (Lógica compartilhada)
         ├── useAuth
         ├── useImoveis
         └── useFavorites
              ↓
API Client (axios)
    ↓
Backend FastAPI
```

---

## 📁 Estrutura de Arquivos

```
frontend/
├── src/
│   ├── app/
│   │   ├── App.tsx              # Componente raiz
│   │   ├── routes.tsx           # Definição de rotas
│   │   └── type.ts              # Tipos globais
│   ├── components/
│   │   ├── ui/                  # Componentes UI base (shadcn/ui)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ... (outros)
│   │   ├── figma/
│   │   │   └── ImageWithFallback.tsx
│   │   ├── ChatAIPage.tsx        # Página de chat
│   │   ├── FavoritesPage.tsx     # Favoritos
│   │   ├── HomePage.tsx          # Home
│   │   ├── LoginPage.tsx         # Login
│   │   ├── MapPage.tsx           # Mapa
│   │   ├── ProfilePage.tsx       # Perfil
│   │   ├── PropertyCard.tsx      # Card de imóvel
│   │   ├── PropertyDetailsPage.tsx # Detalhes
│   │   └── RootLayout.tsx        # Layout raiz
│   ├── styles/
│   │   ├── globals.css           # Estilos globais
│   │   ├── tailwind.css          # Tailwind
│   │   └── theme.css             # Temas (light/dark)
│   └── main.tsx                  # Entry point
├── Dockerfile                    # Build para produção
├── nginx.conf                    # Configuração nginx
├── vite.config.ts               # Configuração Vite
├── tailwind.config.ts           # Configuração Tailwind
├── tsconfig.json                # TypeScript config
├── package.json                 # Dependências Node
├── pnpm-lock.yaml              # Lock file
└── README.md                    # Este arquivo
```

---

## 🔑 Arquivos Principais

### `App.tsx`
Componente raiz:
- Setup de providers (React Query, Auth, etc.)
- Definição de tema (light/dark)
- Error boundaries
- Loading states

### `routes.tsx`
Definição de rotas:
```typescript
const routes = [
  { path: "/", element: <HomePage /> },
  { path: "/login", element: <LoginPage /> },
  { path: "/imoveis", element: <PropertyListPage /> },
  { path: "/imoveis/:id", element: <PropertyDetailsPage /> },
  { path: "/mapa", element: <MapPage /> },
  { path: "/favoritos", element: <FavoritesPage /> },
  { path: "/perfil", element: <ProfilePage /> },
];
```

### `components/LoginPage.tsx`
Autenticação:
- Google OAuth button
- Integração com backend POST /auth/google
- Armazenamento de sessionToken
- Redirecionamento pós-login

### `components/HomePage.tsx`
Dashboard principal:
- Estatísticas (imóveis, preço médio, etc.)
- Trending properties
- Quick filters
- Links para outras seções

### `components/PropertyCard.tsx`
Card reutilizável:
```tsx
interface PropertyCardProps {
  id: number;
  titulo: string;
  preco: number;
  area_m2: number;
  imagem: string;
  classificacao_preco: string; // "Barato" | "Justo" | "Caro"
  onFavorite?: () => void;
}
```

### `components/PropertyDetailsPage.tsx`
Detalhes completos:
- Carousel de imagens
- Informações do imóvel
- Dados da imobiliária
- Mapa de localização
- Ações (favoritar, compartilhar)

---

## 📊 Fluxo de Dados

```
1. User abre app (frontend)
   ↓
2. Verifica sessionToken em localStorage
   ├─ Se válido → Vai para HomePage
   └─ Se não → Vai para LoginPage
   ↓
3. Em LoginPage: clica "Continuar com Google"
   ↓
4. Abre Google OAuth dialog
   ↓
5. Retorna idToken
   ↓
6. Frontend POST /auth/google { idToken }
   ↓
7. Backend retorna sessionToken
   ↓
8. Frontend armazena em localStorage
   ↓
9. Redirecionado para HomePage
   ↓
10. Todas as requisições incluem:
    Authorization: Bearer {sessionToken}
```

---

## 🎨 Componentes UI (shadcn/ui)

O projeto usa **shadcn/ui** para componentes reutilizáveis:

- Button
- Card
- Dialog
- Dropdown Menu
- Form
- Input
- Label
- Select
- Table
- Tabs
- Toast
- etc.

Estilo baseado em **Tailwind CSS** com suporte a temas claro/escuro.

---

## 🚀 Como Rodar

### Pré-requisitos
- **Node.js** 18+
- **pnpm** (package manager)
- **Backend rodando**: `docker compose up -d backend`

### Opção 1: Desenvolvimento Local

```bash
# Entrar na pasta
cd frontend

# Instalar dependências
pnpm install

# Rodar dev server
pnpm run dev

# Abre em http://localhost:5173
```

### Opção 2: Build para Produção

```bash
pnpm run build

# Gera pasta dist/ com arquivos estáticos
```

### Opção 3: Docker

```bash
# Build imagem
docker build -t rentmaster-frontend frontend/

# Rodar container
docker run -p 80:80 rentmaster-frontend

# Abre em http://localhost
```

### Opção 4: Docker Compose

```bash
docker compose up -d frontend

# Abre em http://localhost:3000
```

---

## 🧪 Como Testar

### Teste de Login
1. Abra http://localhost:5173
2. Clique "Continuar com Google"
3. Faça login
4. Deve redirecionar para HomePage ✅

### Teste de Listagem
1. Na HomePage, clique "Ver todos os imóveis"
2. Deve carregar lista de imóveis
3. Cada card exibe título, preço, área, classificação

### Teste de Detalhes
1. Clique em um imóvel
2. Abre PropertyDetailsPage completa
3. Verificar imagens, dados, mapa

### Teste de API Integration
1. Abra DevTools (F12)
2. Vá para Network
3. Clique em um imóvel
4. Veja o request GET /api/imoveis/{id}
5. Verifique response com classificação_preco

---

## 📋 Dependências

Veja `frontend/package.json`:

```json
{
  "dependencies": {
    "react": "^18",
    "react-dom": "^18",
    "react-router-dom": "^6",
    "axios": "^1",
    "@shadcn/ui": "^0.1",
    "tailwindcss": "^3",
    "typescript": "^5"
  },
  "devDependencies": {
    "vite": "^4",
    "@vitejs/plugin-react": "^4",
    "tailwindcss": "^3",
    "postcss": "^8",
    "autoprefixer": "^10"
  }
}
```

---

## 🔐 Segurança

### ✅ Implementado
- Google OAuth 2.0
- SessionToken em localStorage
- HTTPS (em produção)
- CORS configurado no backend

### 🔜 Roadmap
- [ ] Token refresh automático
- [ ] Rate limiting
- [ ] Content Security Policy (CSP)
- [ ] XSS protection

---

## 🎨 Temas e Estilos

### Light Mode (Default)
```css
--background: #ffffff
--foreground: #000000
--primary: #0070f3
```

### Dark Mode
```css
--background: #1a1a1a
--foreground: #ffffff
--primary: #00d9ff
```

Toggle de tema em ProfilePage.

---

## 📊 Páginas Implementadas

### ✅ Completas
- [ ] LoginPage (Google OAuth)
- [ ] HomePage (Dashboard)
- [ ] PropertyCard (componente)
- [ ] RootLayout (navegação)

### 🔜 Em Desenvolvimento
- [ ] PropertyListPage (listagem completa)
- [ ] PropertyDetailsPage (detalhes)
- [ ] MapPage (Google Maps)
- [ ] FavoritesPage (favoritos)
- [ ] ProfilePage (perfil do usuário)
- [ ] ChatAIPage (assistente IA)

---

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| "pnpm not found" | `npm install -g pnpm` |
| Porta 5173 em uso | `pnpm run dev -- --port 3000` |
| API 404 | Verificar URL backend em `.env` |
| Google OAuth falha | Verificar `REACT_APP_GOOGLE_CLIENT_ID` |
| CSS não carrega | `pnpm install && pnpm run dev` |

---

## 🔧 Variáveis de Ambiente

Crie `.env.local`:

```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=seu-client-id.apps.googleusercontent.com
```

---

## 📚 Referências

- [React Docs](https://react.dev)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS](https://tailwindcss.com)
- [shadcn/ui](https://ui.shadcn.com)
- [React Router](https://reactrouter.com)
- [Axios](https://axios-http.com)

---

## 🎯 Próximos Passos

1. Instalar dependências: `pnpm install`
2. Configurar `.env.local`
3. Rodar `pnpm run dev`
4. Testar fluxo de login
5. Testar listagem de imóveis

---

**Status**: ⚠️ Em desenvolvimento (componentes base prontos, integração em andamento)

**Última Atualização**: Setembro 2026
