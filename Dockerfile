# Frontend build stage
FROM node:20 AS frontend-builder
WORKDIR /app/frontend
# Copy package files first (better caching)
COPY frontend/package.json ./
RUN npm install
# Copy source files after dependencies are installed
COPY frontend/ ./
RUN npm run build

# Python build stage
FROM python:3.11-slim AS builder
WORKDIR /app
RUN python -m venv /venv
ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:$PATH"
# Copy the whole project (needed for pyproject.toml to work with src/ structure)
COPY . .
RUN pip install --upgrade pip && pip install .[dev] && pip install --force-reinstall bcrypt==4.0.1

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /venv /venv
ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:$PATH"
COPY src/ src/
COPY config.example.yaml config.yaml
COPY .env.example .env
COPY Makefile .
COPY queue/ /queue/
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist
# Install supervisor, swaks for testing and required tools, then clean up
RUN apt-get update \
    && apt-get install -y --no-install-recommends supervisor swaks make \
    && mkdir -p /var/log/supervisor \
    && rm -rf /var/lib/apt/lists/*
RUN useradd -m appuser && chown -R appuser /app && chmod -R 700 /app
EXPOSE 2525 8080 8000
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
