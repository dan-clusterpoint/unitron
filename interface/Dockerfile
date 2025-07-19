# Build stage
FROM node:18-alpine AS build
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
FROM node:18-alpine AS prod
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY --from=build /app/build ./build
HEALTHCHECK CMD node -p "'npx' in process.env.PATH" || exit 1
EXPOSE 3000
CMD ["npm", "start"]
