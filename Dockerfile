FROM python:3.11-slim AS builder
WORKDIR /app
RUN python -m venv /venv
ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:$PATH"
COPY pyproject.toml .
RUN pip install --upgrade pip && pip install .[dev]

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
RUN useradd -m appuser && chown -R appuser /app && chmod -R 700 /app
USER appuser
EXPOSE 2525 8080
CMD ["python", "-m", "signalhub.app"]
