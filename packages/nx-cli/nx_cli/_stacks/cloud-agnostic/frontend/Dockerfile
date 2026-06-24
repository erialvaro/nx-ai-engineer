# syntax=docker/dockerfile:1
# Multi-stage, non-root, pinned base, Next.js standalone output.
FROM node:20-slim AS deps
WORKDIR /app
COPY package.json ./
RUN npm install

FROM node:20-slim AS dev
WORKDIR /app
ENV NODE_ENV=development
RUN addgroup --system app && adduser --system --ingroup app app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN chown -R app:app /app
USER app
EXPOSE 3000
CMD ["npm", "run", "dev"]

FROM node:20-slim AS build
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-slim AS prod
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1
RUN addgroup --system app && adduser --system --ingroup app app
COPY --from=build /app/public ./public
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
USER app
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/',r=>process.exit(r.statusCode<500?0:1)).on('error',()=>process.exit(1))"
CMD ["node", "server.js"]
