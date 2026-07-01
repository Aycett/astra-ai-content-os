# Astra AI Content OS — Backend

Modular monolith API for Astra AI Content OS.

See [MASTER_CONTEXT.md](../MASTER_CONTEXT.md) and [docs/SYSTEM_ARCHITECTURE.md](../docs/SYSTEM_ARCHITECTURE.md) for architectural context.

## Requirements

- Python 3.14+
- pip

For Docker-based runs: Docker and Docker Compose.

## Configuration

Copy the environment template from the repository root:

```bash
cp ../.env.example .env
```

Or for Docker Compose, copy to the repository root:

```bash
cp .env.example .env
```

Edit `.env` and set `POSTGRES_PASSWORD` and connection URLs. Never commit `.env` to version control.

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `POSTGRES_*` | PostgreSQL credentials and port (used by Docker Compose) |
| `REDIS_PORT` | Redis host port mapping for Docker Compose |

## Run locally (without Docker)

From the `backend/` directory:

```bash
python -m venv .venv
```

Activate the virtual environment:

**Windows (PowerShell)**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install dependencies and start the server:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API runs without PostgreSQL or Redis connected. Database and cache clients are not wired yet.

## Run with Docker Compose

From the repository root:

```bash
cp .env.example .env
docker compose up --build
```

This starts:

| Service | Purpose |
|---------|---------|
| `backend` | FastAPI application (uvicorn) |
| `postgres` | PostgreSQL 17 |
| `redis` | Redis 7 |

Docker Compose overrides `DATABASE_URL` and `REDIS_URL` for the backend container to use service hostnames (`postgres`, `redis`).

Run in detached mode:

```bash
docker compose up --build -d
```

Stop services:

```bash
docker compose down
```

## Health check

**URL:** `GET http://localhost:8000/health`

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "Astra AI Content OS",
  "version": "0.1.0",
  "environment": "local"
}
```

Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Project layout

```
backend/
├── app/
│   ├── main.py           # FastAPI app factory
│   ├── api/routes/       # HTTP route handlers
│   ├── core/             # Configuration and shared infrastructure
│   └── schemas/          # Pydantic request/response models
├── requirements.txt
├── .dockerignore
└── README.md
```

## Scope

**Implemented:** API shell, health endpoint, typed configuration, Docker Compose infrastructure.

**Not yet implemented:** Database models, migrations, Redis clients, agents, authentication, AI providers, publishing.
