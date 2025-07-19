# Build stage
FROM node:20 AS build
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
# Clean up stray cache folder if present
RUN rm -rf node_modules/.cache || true
RUN npm ci

# Copy source
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine AS prod
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
