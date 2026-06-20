# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Instalar pnpm globalmente
RUN npm install -g pnpm

# Copiar os arquivos de manifesto e dependências
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml* ./

# Instalar dependências usando pnpm
RUN pnpm install

# Copiar o restante do código-fonte
COPY . .

# Build da aplicação
RUN pnpm run build

# Production stage
FROM nginx:alpine

# Remover configuração padrão do Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copiar a configuração customizada do Nginx do projeto
COPY nginx.conf /etc/nginx/conf.d/rentmaster.conf

# Copiar os arquivos buildados da etapa anterior
COPY --from=builder /app/dist /usr/share/nginx/html/

# Healthcheck para garantir que o container está saudável
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=2 \
    CMD wget --quiet --tries=1 --spider http://localhost:80 || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]