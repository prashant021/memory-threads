FROM node:18-alpine
WORKDIR /app
COPY package.json ./
RUN npm install --legacy-peer-deps
COPY . .
# create empty .next directory with permissions
RUN mkdir -p .next && chmod -R 777 .next
CMD ["npm", "run", "dev"]
