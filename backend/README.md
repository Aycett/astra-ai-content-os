# Astra AI Content OS — Backend

Modular monolith API for Astra AI Content OS.

See [MASTER_CONTEXT.md](../MASTER_CONTEXT.md) and [docs/SYSTEM_ARCHITECTURE.md](../docs/SYSTEM_ARCHITECTURE.md) for architectural context.

## Requirements

- Python 3.14+
- pip

For Docker-based runs: Docker and Docker Compose.

## Configuration

The project uses a **single** environment file at the repository root:

```
astra-ai-content-os/.env
```

Create it from the template:

```bash
cp .env.example .env
```

Run this from the repository root (`astra-ai-content-os/`). Do not create `backend/.env`.

The backend loads this file automatically regardless of your current working directory. Docker Compose also reads the same root `.env`.

Edit `.env` and set `POSTGRES_PASSWORD` and other values as needed. Never commit `.env` to version control.

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `POSTGRES_*` | PostgreSQL credentials and port (used by Docker Compose) |
| `REDIS_PORT` | Redis host port mapping for Docker Compose |
| `TAVILY_API_KEY` | Optional Tavily Search API key for live research |

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

## Run ResearchAgent locally

From the `backend/` directory with the virtual environment activated.

### Mock provider (no API key)

Leave `TAVILY_API_KEY` empty. Research falls back to `MockResearchProvider`.

```bash
python -c "from uuid import uuid4; from app.agents import AgentContext, ResearchAgent; ctx = AgentContext(request_id=uuid4(), topic='AI productivity tools'); result = ResearchAgent().run(ctx); print(result.model_dump_json(indent=2))"
```

**Windows (PowerShell):**

```powershell
python -c "from uuid import uuid4; from app.agents import AgentContext, ResearchAgent; ctx = AgentContext(request_id=uuid4(), topic='AI productivity tools'); result = ResearchAgent().run(ctx); print(result.model_dump_json(indent=2))"
```

### Tavily provider

1. Sign up at [tavily.com](https://tavily.com) and create an API key.
2. Add the key to the repository root `.env`:

```bash
TAVILY_API_KEY=tvly-your-key-here
```

3. Run the same test command. Provider order is:

   1. `TavilyProvider` (live search)
   2. `MockResearchProvider` (fallback if Tavily fails or returns no results)

```bash
python -c "from uuid import uuid4; from app.agents import AgentContext, ResearchAgent; ctx = AgentContext(request_id=uuid4(), topic='AI productivity tools'); result = ResearchAgent().run(ctx); print(result.model_dump_json(indent=2))"
```

Check `data.research.provider_used` in the output — `tavily` means live results, `mock` means fallback was used.

Each source includes a `score` field (0–1) from deterministic trend scoring, sorted highest first:

| Rule | Points |
|------|--------|
| Base score | +0.1 |
| Has URL | +0.2 |
| Query words in title | +0.4 |
| Query words in snippet | +0.3 |

Maximum score is capped at 1.0.

### Trend candidates

After scoring, `ResearchAgent` returns `data.candidates` — up to 5 `TrendCandidate` objects with video-friendly titles, angles, source references, and reasoning. No AI provider is used.

### Content brief generator

Convert trend candidates into `ContentBrief` objects:

```bash
python -c "from uuid import uuid4; from app.agents import AgentContext, ResearchAgent; from app.services.planning import generate_briefs; from app.services.research.models import TrendCandidate; ctx = AgentContext(request_id=uuid4(), topic='AI productivity tools'); research = ResearchAgent().run(ctx); candidates = [TrendCandidate.model_validate(c) for c in research.data['candidates']]; briefs = generate_briefs(candidates, topic='AI productivity tools'); print(briefs[0].model_dump_json(indent=2))"
```

**Windows (PowerShell):** use the same command.

### Script package generator

Convert a `ContentBrief` into a `ScriptPackage`:

```bash
python -c "from uuid import uuid4; from app.agents import AgentContext, ResearchAgent; from app.services.planning import generate_briefs; from app.services.script import generate_script; ctx = AgentContext(request_id=uuid4(), topic='AI productivity tools'); research = ResearchAgent().run(ctx); briefs = generate_briefs(research.data['candidates'], topic='AI productivity tools'); script = generate_script(briefs[0]); print(script.model_dump_json(indent=2))"
```

**Windows (PowerShell):** use the same command.

### ScriptAgent

Run the script agent with a brief in context metadata:

```bash
python -c "from uuid import uuid4; from app.agents import AgentContext, ResearchAgent, ScriptAgent; from app.services.planning import generate_briefs; ctx = AgentContext(request_id=uuid4(), topic='AI productivity tools'); research = ResearchAgent().run(ctx); briefs = generate_briefs(research.data['candidates'], topic='AI productivity tools'); script_ctx = AgentContext(request_id=ctx.request_id, metadata={'brief': briefs[0].model_dump(mode='json')}); result = ScriptAgent().run(script_ctx); print(result.model_dump_json(indent=2))"
```

**Windows (PowerShell):** use the same command.

### Voice package generator

Convert a `ScriptPackage` into a `VoicePackage`:

```bash
python -c "from uuid import uuid4; from app.agents import AgentContext, ResearchAgent, ScriptAgent; from app.services.planning import generate_briefs; from app.services.voice import generate_voice_package; ctx = AgentContext(request_id=uuid4(), topic='AI productivity tools'); research = ResearchAgent().run(ctx); briefs = generate_briefs(research.data['candidates'], topic='AI productivity tools'); script = ScriptAgent().run(AgentContext(request_id=ctx.request_id, metadata={'brief': briefs[0].model_dump(mode='json')})); voice = generate_voice_package(script.data['script']); print(voice.model_dump_json(indent=2))"
```

**Windows (PowerShell):** use the same command.

### VoiceAgent

Run the voice agent with a script in context metadata:

```bash
python -c "from uuid import uuid4; from app.agents import AgentContext, ResearchAgent, ScriptAgent, VoiceAgent; from app.services.planning import generate_briefs; ctx = AgentContext(request_id=uuid4(), topic='AI productivity tools'); research = ResearchAgent().run(ctx); briefs = generate_briefs(research.data['candidates'], topic='AI productivity tools'); script = ScriptAgent().run(AgentContext(request_id=ctx.request_id, metadata={'brief': briefs[0].model_dump(mode='json')})); voice = VoiceAgent().run(AgentContext(request_id=ctx.request_id, metadata={'script': script.data['script']})); print(voice.model_dump_json(indent=2))"
```

**Windows (PowerShell):** use the same command.

### Scene plan generator

Convert a `ScriptPackage` into a `ScenePlan`:

```bash
python -c "from uuid import uuid4; from app.agents import AgentContext, ResearchAgent, ScriptAgent; from app.services.planning import generate_briefs; from app.services.scene import generate_scene_plan; ctx = AgentContext(request_id=uuid4(), topic='AI productivity tools'); research = ResearchAgent().run(ctx); briefs = generate_briefs(research.data['candidates'], topic='AI productivity tools'); script = ScriptAgent().run(AgentContext(request_id=ctx.request_id, metadata={'brief': briefs[0].model_dump(mode='json')})); plan = generate_scene_plan(script.data['script']); print(plan.model_dump_json(indent=2))"
```

**Windows (PowerShell):** use the same command.

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
│   ├── agents/           # Domain agents (research, script, etc.)
│   ├── services/         # Service layer (research providers, etc.)
│   └── schemas/          # Pydantic request/response models
├── requirements.txt
├── .dockerignore
└── README.md
```

## Scope

**Implemented:** API shell, health endpoint, typed configuration, Docker Compose infrastructure, agent framework, research provider framework, Tavily research provider, trend scoring v0.1, trend candidate generator, content brief generator, script package generator, ScriptAgent, voice package generator, VoiceAgent, scene plan generator.

**Not yet implemented:** Database models, migrations, Redis clients, authentication, AI providers, publishing.
