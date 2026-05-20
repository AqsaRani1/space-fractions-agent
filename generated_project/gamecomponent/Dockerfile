FROM node:18-20-alpine

# Install dependencies
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Set environment variables
ENV PORT=${THIS_COMPONENT.port}
ENV POSTGRES_HOST=<postgres-host>
ENV POSTGRES_DB=<postgres-database>
ENV POSTGRES_USER=<postgres-user>
ENV POSTGRES_PASSWORD=<postgres-password>
ENV REDIS_HOST=<redis-host>
ENV REDIS_PORT=<redis-port>

# # FR-1: Play game
# # NFR-1: Secure authentication
EXPOSE ${THIS_COMPONENT.port}
CMD ["npm", "start"]