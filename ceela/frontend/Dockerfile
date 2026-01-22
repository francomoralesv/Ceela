# Etapa 1: Construcción
FROM node:20-slim AS builder
WORKDIR /app

# Argumentos de construcción para variables de entorno
ARG NEXT_PUBLIC_API_ENDPOINT
ARG NEXT_PUBLIC_APP_NAME
ARG AWS_PLACE_INDEX_NAME
ARG PLACES_API_KEY

# Establecer variables de entorno para el build
ENV NEXT_PUBLIC_API_ENDPOINT=$NEXT_PUBLIC_API_ENDPOINT
ENV NEXT_PUBLIC_APP_NAME=$NEXT_PUBLIC_APP_NAME
ENV AWS_PLACE_INDEX_NAME=$AWS_PLACE_INDEX_NAME
ENV PLACES_API_KEY=$PLACES_API_KEY

COPY package.json yarn.lock ./
RUN yarn install && yarn cache clean

COPY . . 
RUN yarn build


FROM node:20-slim
WORKDIR /app

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/yarn.lock ./yarn.lock
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["yarn", "start"]
