FROM node:14-alpine

# Install application dependencies
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Build production-ready app
RUN npm run build

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000

# Start the application
CMD ["npm", "start"]