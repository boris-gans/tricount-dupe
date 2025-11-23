FROM node:23 AS build

WORKDIR /app

# Allow API base URL to be injected at build time
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Copy package files first
COPY package*.json ./

# Install dependencies (legacy-peer-deps makes it more tolerant)
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

# Build Vite app
RUN npm run build

# Production server: nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
