# Usamos la versión 22 de Node.js
FROM node:22-alpine

WORKDIR /app

# Copiamos dependencias
COPY package.json package-lock.json ./

# Instalamos los paquetes de npm
RUN npm install

# Copiamos el resto del código Svelte
COPY . .

# Exponemos el puerto de SvelteKit
EXPOSE 5173

# Vite necesita el flag --host para ser visible fuera del contenedor
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]