FROM node:18-20-alpine

# Install dependencies
COPY package*.json ./
RUN npm ci --production

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Set the working directory
WORKDIR /app

# Expose the port
EXPOSE ${PORT}

# Start the application
CMD ["npm", "start"]