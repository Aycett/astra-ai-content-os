# Astra AI Content OS — Backend

Modular monolith API for Astra AI Content OS (Milestone 4: Foundation).

See [MASTER_CONTEXT.md](../MASTER_CONTEXT.md) and [docs/SYSTEM_ARCHITECTURE.md](../docs/SYSTEM_ARCHITECTURE.md) for architectural context.

## Requirements

- Python 3.14+
- pip

## Local setup

From the repository root:

```bash
cd backend
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

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy environment template into `backend/`:

```bash
cp ../.env.example .env
```

Edit `.env` as needed. Defaults are suitable for local development.

## Run the server

From the `backend/` directory:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use values from `.env`:

```bash
uvicorn app.main:app --reload --host %HOST% --port %PORT%
```

On macOS/Linux, use `$HOST` and `$PORT` instead of `%HOST%` and `%PORT%`.

## Verify

Health check:

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
└── README.md
```

## Scope (v0.1 foundation)

This milestone includes only the API shell and health endpoint. Database, Redis, agents, authentication, and external integrations are not implemented yet.
