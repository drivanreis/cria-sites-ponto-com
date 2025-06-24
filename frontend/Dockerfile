# File: frontend/Dockerfile

# FROM node:20-alpine AS builder
FROM node:20-alpine

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de configuração do projeto
COPY package.json package-lock.json* ./

# Instala as dependências
RUN npm ci

# Remove o comando de build (ele é para produção)
# REMOVA: RUN npm run build

# Nao precisa instalar 'serve'
# REMOVA: RUN npm install -g serve
# REMOVA: COPY --from=builder /app/dist ./dist
COPY . .

EXPOSE 3000

# Comando para iniciar o servidor 'serve' na porta 3000, servindo a pasta 'dist'
# CMD ["serve", "-s", "dist", "-l", "3000"]

# Comando para iniciar o servidor de desenvolvimento do Vite
CMD ["npm", "run", "dev"]