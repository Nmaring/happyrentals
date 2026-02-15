# Build frontend, then serve with Caddy
FROM node:20-alpine AS build
WORKDIR /src

COPY frontend/package*.json /src/
RUN npm ci

COPY frontend/ /src/
RUN npm run build

FROM caddy:2-alpine
WORKDIR /srv
COPY --from=build /src/dist /srv
COPY deploy/Caddyfile /etc/caddy/Caddyfile
