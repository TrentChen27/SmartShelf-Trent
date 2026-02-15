FROM node:22-alpine3.22 AS builder

WORKDIR /app
ENV NODE_ENV=production

# Copy package files
COPY Frontend/package*.json ./

# Install dependencies
RUN npm ci --include=dev --silent

# copy source code
COPY Frontend/ ./

# Build for production
RUN npm run build --silent

# Production stage
FROM nginx:stable-alpine

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY Frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
