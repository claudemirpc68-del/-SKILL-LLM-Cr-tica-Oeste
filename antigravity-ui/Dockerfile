# Estágio de Build
FROM node:18-slim AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
# A variável de ambiente pode ser injetada no build ou no runtime via docker-compose/coolify
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Estágio de Produção
FROM nginx:stable-alpine

COPY --from=build /app/dist /usr/share/nginx/html

# Configuração customizada do Nginx para lidar com roteamento do React (SPA)
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
