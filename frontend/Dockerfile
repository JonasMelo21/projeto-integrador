# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar package files
COPY codigo_figma/package*.json ./

# Instalar dependências
RUN npm install

# Copiar arquivos de configuração
COPY codigo_figma/vite.config.ts ./
COPY codigo_figma/tsconfig.json ./
COPY codigo_figma/tsconfig.node.json ./
COPY codigo_figma/tailwind.config.ts ./
COPY codigo_figma/postcss.config.mjs ./
COPY codigo_figma/index.html ./
COPY codigo_figma/default_shadcn_theme.css ./

# Copiar source code
COPY codigo_figma/src ./src

# Build
RUN npm run build

# Production stage
FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/rentmaster.conf
COPY --from=builder /app/dist /usr/share/nginx/html/

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=2 \
    CMD wget --quiet --tries=1 --spider http://localhost:80 || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
