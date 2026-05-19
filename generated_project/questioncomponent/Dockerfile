FROM node:16

# Install dependencies
RUN npm install -g npm@latest
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Set the startup command
CMD ["npm", "start"]

# Set the port to listen on
EXPOSE 3000