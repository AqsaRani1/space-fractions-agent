FROM node:14

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Build the application
RUN npm run build

# Run the application
CMD ["npm", "start"]

EXPOSE 3000