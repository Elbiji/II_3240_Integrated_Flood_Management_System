FROM node:20-alpine
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy everything else (including your src/pages folders)
COPY . .

EXPOSE 3000

# Start in dev mode
CMD ["npm", "run", "dev"]