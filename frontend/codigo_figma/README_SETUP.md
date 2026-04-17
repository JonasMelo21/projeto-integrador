# ImóvelHub Frontend

Frontend React com Vite para a aplicação ImóvelHub.

## Setup Rápido

### Pré-requisitos
- Node.js 18+
- npm ou pnpm
- FastAPI backend rodando em `http://localhost:8000`

### Instalação

```bash
npm install
```

### Desenvolvimento

```bash
npm run dev
```

O projeto abrirá em `http://localhost:5173`

### Build para Produção

```bash
npm run build
```

## Estrutura do Projeto

```
src/
├── app/
│   ├── components/          # Componentes React
│   │   ├── HomePage.tsx    # Lista de imóveis
│   │   ├── PropertyDetailsPage.tsx  # Detalhes do imóvel
│   │   ├── PropertyCard.tsx # Card do imóvel
│   │   ├── RootLayout.tsx  # Layout principal
│   │   ├── figma/          # Componentes Figma
│   │   └── ui/             # Componentes shadcn UI
│   ├── services/
│   │   └── api.ts          # Serviço de chamadas à API FastAPI
│   ├── data/
│   │   └── mockData.ts     # Dados de exemplo (não utilizado)
│   ├── App.tsx
│   ├── routes.tsx          # Configuração de rotas
│   └── styles/
│       └── index.css       # Estilos globais
└── main.tsx                # Entrada da aplicação

```

## API Integration

O frontend se conecta à API FastAPI em `http://localhost:8000/api`

Endpoints utilizados:
- `GET /api/imoveis` - Lista imóveis
- `GET /api/imoveis/{id}` - Detalhes do imóvel
- `GET /api/imoveis/by-hex/{id_hex}` - Imóvel por ID único
- `GET /api/imoveis/stats` - Estatísticas

## Tecnologias

- **React 18.3** - UI Library
- **Vite 6.3** - Build tool
- **Tailwind CSS 4.1** - Styling
- **React Router 7.13** - Routing
- **shadcn/ui** - Component library
- **Recharts 2.15** - Gráficos
- **Lucide React** - Ícones

## Configuração Vite

O Vite está configurado com:
- Proxy para `/api` → `http://localhost:8000`
- Suporte a Tailwind CSS
- Plugin React com Fast Refresh
- Alias `@` para `src/`

## Desenvolvendo

### Adicionar novo componente

1. Criar arquivo em `src/app/components/NovoComponente.tsx`
2. Adicionar rota em `src/app/routes.tsx` (se necessário)
3. Importar e usar no layout

### Estilização

Use Tailwind CSS classes. As cores seguem o tema definido em `default_shadcn_theme.css`

### Chamadas à API

Use o serviço em `src/app/services/api.ts`:

```typescript
import { api } from '../services/api'

const properties = await api.getProperties(50, 0)
```

## Troubleshooting

### "Cannot find module '@radix-ui/react-slot'"

Solução: O módulo é uma dependência indireta. Execute `npm install` novamente.

### FastAPI cors error

Certifique-se que o FastAPI backend tem CORS habilitado:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Deploy

1. Build o projeto: `npm run build`
2. Deploy a pasta `dist/` para um servidor web
3. Configure variáveis de ambiente para apontar à API correta
