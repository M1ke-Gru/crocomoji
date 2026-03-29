FROM node:22-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ARG VITE_API_URL=/jokestar/api
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build -- --base=/jokestar/

# Tiny init image — copies built files to a mounted volume on startup
FROM alpine:3
COPY --from=build /app/dist /app/dist
ENTRYPOINT ["sh", "-c", "cp -r /app/dist/. /dist/ && echo 'Frontend ready'"]
