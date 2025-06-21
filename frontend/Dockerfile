# File: frontend/Dockerfile

FROM node:20-alpine AS builder

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de configuração do projeto
COPY package.json package-lock.json* ./

# Instala as dependências
RUN npm ci

# Copia o restante dos arquivos da aplicação
COPY . .

# Constrói a aplicação Vite para produção
# O comando 'npm run build' compilará seu código React/TypeScript
# e gerará os arquivos estáticos na pasta 'dist' (padrão do Vite)
RUN npm run build

# Estágio de Servidor (Produção - Apenas o necessário)
# Usa uma imagem Node.js leve para servir os arquivos estáticos
FROM node:20-alpine

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de build gerados pelo estágio 'builder'
COPY --from=builder /app/dist ./dist

# Para servir os arquivos estáticos de forma simples e leve,
# podemos usar o 'serve' (um pacote npm leve para servir estáticos).
# Primeiro, instale o 'serve' globalmente.
RUN npm install -g serve

# Expõe a porta que o 'serve' irá escutar (padrão é 3000 ou 5000)
# Você pode definir a porta que quiser, mas 3000 é comum para frontends.
EXPOSE 3000

# Comando para iniciar o servidor 'serve' na porta 3000, servindo a pasta 'dist'
CMD ["serve", "-s", "dist", "-l", "3000"]