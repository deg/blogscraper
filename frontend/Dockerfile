FROM node:22.2-alpine
WORKDIR /app

RUN yarn global add vite
COPY package.json ./
RUN yarn install
COPY . .

# CMD ["yarn", "dev"]
# Replace with this, when you need to "docker compose exec dashboard" into a broken container
# CMD ["tail", "-f", "/dev/null"]
