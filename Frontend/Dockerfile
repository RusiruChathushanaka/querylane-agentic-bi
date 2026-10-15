FROM node:26-bookworm-slim AS dependencies
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:26-bookworm-slim AS build
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:26-bookworm-slim
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0
RUN groupadd --gid 10001 appuser && useradd --uid 10001 --gid appuser appuser
COPY --from=build --chown=appuser:appuser /app/.next/standalone ./
COPY --from=build --chown=appuser:appuser /app/.next/static ./.next/static
COPY --from=build --chown=appuser:appuser /app/public ./public
USER appuser
EXPOSE 8080
CMD ["node", "server.js"]
