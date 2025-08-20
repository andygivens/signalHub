# SignalHub

SignalHub is a lightweight, extensible notification bridge that receives events over SMTP and forwards them to Pushover via HTTPS. Designed for home labs and automation, it is future-friendly for additional inputs/outputs.

## Features
- Accepts SMTP from LAN apps, converts to Pushover notifications
- Configurable via environment variables and YAML
- Secure defaults: loopback bind, optional STARTTLS/AUTH
- Rate limiting, deduplication, retry/backoff, file queue
- Structured JSON logging
- Health and metrics HTTP server
- Easy to run locally or via Docker

## Quickstart

### Docker Compose
```sh
docker compose up
```

### Bare Python
```sh
python -m venv .venv
. .venv/bin/activate
pip install .[dev]
python -m signalhub.app
```

### Send a test email
```sh
swaks --server localhost:2525 --to alerts@home.local --from app@lab --header "Subject: Test [PRIO=1] [URL=https://example.com] [URLTITLE=Open]" --data "Body line"
```

## Configuration

### Environment Variables
| Variable                | Description                  |
|-------------------------|------------------------------|
| PUSHOVER_TOKEN          | Pushover app token           |
| PUSHOVER_USER_KEY       | Default user/group key       |
| PUSHOVER_DEVICE         | Device name (optional)       |
| SMTP_HOST               | SMTP listen host             |
| SMTP_PORT               | SMTP listen port             |
| SMTP_ALLOW_NOAUTH       | Allow unauthenticated SMTP   |
| SMTP_USER               | SMTP AUTH username           |
| SMTP_PASS               | SMTP AUTH password           |
| TLS_CERT_FILE           | TLS cert file (optional)     |
| TLS_KEY_FILE            | TLS key file (optional)      |
| HTTP_HEALTH_PORT        | Health server port           |
| RATE_LIMIT_PER_MINUTE   | Rate limit per minute        |
| QUEUE_DIR               | Directory for failed queue   |

### YAML Example
See `config.example.yaml` for structure.

## Health & Metrics
- `GET /healthz` → 200 OK
- `GET /metrics` → JSON counters

## Testing & Lint
```sh
make test
make lint
```

## Security Notes
- Default bind: 127.0.0.1 (change for LAN)
- Use firewall for external access
- Enable STARTTLS/AUTH for WAN

## Troubleshooting
- Bad tokens: check PUSHOVER_TOKEN
- Auth errors: check SMTP_USER/PASS
- Rate limit: adjust RATE_LIMIT_PER_MINUTE
- TLS: set TLS_CERT_FILE/TLS_KEY_FILE

## Architecture
```mermaid
flowchart LR
  A[Home Lab App\nSMTP Client] -->|HELO/MAIL/RCPT/DATA| B[SignalHub\n(aiosmtpd)]
  B --> C{Parser & Router}
  C -->|Subject/Body| D[Pushover Builder]
  D -->|HTTPS POST| E[Pushover API]
  E -->|Push| F[iPhone]
  C -->|Fail/Retry| G[Backoff & Queue]
  B --> H[Healthz/Metrics]
```

## License
MIT
