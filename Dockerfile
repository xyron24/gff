# Multi-Stage Dockerfile for Mastercard AI Defense Lab

# Stage 1: Build Next.js Web Dashboard
FROM node:20-alpine AS frontend-builder
WORKDIR /app/web
COPY web/package*.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

# Stage 2: Python Backend & Unified Production Runtime
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Backend and Taxonomy Code
COPY identify/ ./identify/
COPY generate/ ./generate/
COPY defend/ ./defend/
COPY closed_loop/ ./closed_loop/
COPY data/ ./data/
COPY api/ ./api/
COPY pyproject.toml .env.example ./

# Copy Frontend Artifacts
COPY --from=frontend-builder /app/web/.next /app/web/.next
COPY --from=frontend-builder /app/web/public /app/web/public
COPY --from=frontend-builder /app/web/package*.json /app/web/
COPY --from=frontend-builder /app/web/node_modules /app/web/node_modules

EXPOSE 8000
EXPOSE 3000

ENV PORT=8000
ENV HOST=0.0.0.0

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port 8000 & cd web && npm start"]
