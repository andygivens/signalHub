SignalHub Planning

Dev API Hostname
- All API and frontend URLs should use: http://docker3.home.agivens.io:8124

Deployment Requirement
- The app must run as a single container for simple deployment and packaging. No separate frontend or backend containers.

Dev Workflow Shortcuts
- Use `make dev-rebuild` to rebuild and start the dev container.
- Use `make dev-api` inside the dev container to start FastAPI with hot reload.

Goal
- Add an admin API and simple web frontend to manage SMTP, Pushover, mappings, templates, and queued messages.
- Simple, single-container deployment for easy install and use.

Tech choices
- Backend: FastAPI (async, OpenAPI)
- DB: SQLite for initial storage (SQLModel/SQLAlchemy)
- Frontend: React + Vite (built as static files, served by backend)
- Auth: single admin account (password hashed) + optional API keys

Milestones
1) Scaffold FastAPI service and DB models (AdminUser, Settings, Mapping, Template, QueueRecord) [x]
2) Implement auth (bootstrap admin from .env, force rotation) and session cookie + API key endpoints [x]
3) Settings API + UI for SMTP and Pushover (validate tokens) [x]
4) Mapping CRUD + template editor and preview [x]
5) Queue browser + replay + logs page [x]
6) Integrate send/test endpoint and connect to existing handler logic [x]
7) Tests, CI, Docker compose (single container), docs [ ]

Short-term TODOs
- [x] Container-based dev workflow (dev service, src/ mount, .env, port 8124)
- [x] Add Makefile target: make dev (starts dev container)
- [x] Implement /api/login endpoint (admin authentication)
- [x] Add session or token-based auth for protected endpoints
- [x] Add endpoints: /api/settings, /api/mappings, /api/templates, /api/queue, /api/test
- [x] Add CRUD endpoints for mappings and templates (add, update, delete)
- [x] Build frontend as static files (npm run build)
- [x] Update backend to serve static files (React build) via FastAPI
- [x] Update Dockerfile to build frontend and copy static files into image
- [x] Remove separate frontend service from docker-compose.yml
- [x] Update documentation for single-container deployment
- [ ] Test single-container deployment end-to-end (frontend + API + auth)
- [ ] Add API key generation and display (one-time show only)
- [ ] Add tests and CI for API endpoints
- [ ] Wire settings persistence (store non-secret settings in DB; secrets read from env)
- [ ] Integrate signalhub logic (SMTP bridge) into FastAPI app or as background task

Notes & conventions
- All development should happen inside the dev container. No local Python/venv needed on host.
- Do not commit secrets. Keep PUSHOVER_TOKEN and PUSHOVER_USER_KEY in .env or secret store.
- Persist admin password hash to DB; initial ADMIN_PASS set via .env; require rotate on first login.
- Provide `make dev` target to run backend and frontend in development mode.

Next action
- Wire the settings API to the actual SMTP server and notification logic so settings changes take effect.
- Create proper UI pages for mappings, templates, and queue management (currently just API test buttons).
- Add API key generation for external access.