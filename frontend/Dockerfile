FROM node:22.14.0-alpine3.21 AS builder
WORKDIR /build
COPY package*.json ./
RUN npm install --no-audit --no-fund
COPY tsconfig*.json vite.config.ts index.html .eslintrc.cjs ./
COPY src ./src
RUN npm run build

FROM nginx:1.27.4-alpine AS runtime
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /build/dist /usr/share/nginx/html
RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx
USER nginx
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s --retries=3 CMD ["wget", "-qO-", "http://127.0.0.1:8080/healthz"]
ENTRYPOINT []
CMD ["nginx", "-g", "daemon off;"]
