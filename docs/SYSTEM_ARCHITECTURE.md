# Astra AI Content OS — System Architecture

**Version:** 1.0  
**Status:** Architecture Reference  
**Last Updated:** July 2026  
**Parent Document:** [MASTER_CONTEXT.md](../MASTER_CONTEXT.md)

---

## Document Purpose

This document describes the **system architecture** of Astra AI Content OS at an enterprise design level. It translates the principles, constraints, and technology decisions defined in **MASTER_CONTEXT.md** into a concrete structural blueprint.

This document is **implementation-independent**. It defines responsibilities, boundaries, data flows, and integration patterns — not source code, schemas, or deployment manifests.

When architectural ambiguity arises, **MASTER_CONTEXT.md** is authoritative. This document must remain aligned with it at all times.

---

## 1. High Level Architecture

Astra AI Content OS is a **Modular Monolith with Service Boundaries**. All backend capabilities deploy as a single application (`backend/`) with strict internal module boundaries. The system is not decomposed into independently deployed microservices in v1.0.

The platform serves three primary actors:

| Actor | Role |
|-------|------|
| **Operators** | Configure workspaces, review content, approve publishes via the dashboard |
| **AI Agents** | Execute autonomous research, creation, publishing, and learning workflows |
| **External Platforms** | Receive published content and return analytics via platform adapters |

### System Topology

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           OPERATORS                                      │
│                     (frontend/ — Admin Dashboard)                        │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │ HTTPS / REST
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     MODULAR MONOLITH (backend/)                          │
│                                                                          │
│  ┌─────────────┐  ┌──────────────────────────────────────────────────┐  │
│  │  API Layer  │  │              Master Orchestrator                  │  │
│  │  (FastAPI)  │──│         (LangGraph — Pipeline State Machine)       │  │
│  └─────────────┘  └───────────────────────┬──────────────────────────┘  │
│                                           │                              │
│  ┌────────────────────────────────────────┴──────────────────────────┐  │
│  │                        BACKEND MODULES                             │  │
│  │  Research │ Trend │ Planning │ Script │ Voice │ Visual │ Video   │  │
│  │  Subtitle │ Quality │ Publishing │ Analytics                       │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                           │                              │
│  ┌────────────────────────────────────────┴──────────────────────────┐  │
│  │                         AI LAYER                                   │  │
│  │              Provider Abstraction (OpenAI · Anthropic · Google)    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└──────────┬──────────────────┬──────────────────┬────────────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────────┐
    │ PostgreSQL  │    │    Redis    │    │      Storage Layer          │
    │  (Metadata) │    │ Queue/Cache │    │  Assets · Videos · Logs     │
    └─────────────┘    └─────────────┘    └─────────────────────────────┘
                                                      │
                                                      ▼
                              ┌───────────────────────────────────────────┐
                              │         EXTERNAL INTEGRATIONS              │
                              │   YouTube Shorts · TikTok · Instagram Reels│
                              └───────────────────────────────────────────┘
```

### Architectural Layers

| Layer | Responsibility |
|-------|----------------|
| **Presentation** | Operator dashboard for configuration, monitoring, and approval |
| **API** | External-facing HTTP interface; request validation and routing |
| **Orchestration** | Pipeline coordination, state management, gates, and retries |
| **Domain Modules** | Bounded business capabilities with strict internal contracts |
| **AI Layer** | Provider-agnostic model invocation, routing, and fallback |
| **Data** | Persistent metadata, ephemeral job state, and binary asset storage |
| **Integration** | Platform adapters for publish and analytics APIs |

### Canonical Artifacts

Modules communicate through versioned, validated artifacts — not shared mutable state:

| Artifact | Producer | Consumer |
|----------|----------|----------|
| **Topic Candidate** | Research Module | Trend Module |
| **Ranked Topic List** | Trend Module | Planning Module |
| **Content Brief** | Planning Module | Script Module |
| **Script Package** | Script Module | Quality Module, Voice Module |
| **Render Manifest** | Visual Module, Voice Module | Video Module |
| **Final Video** | Video Module, Subtitle Module | Quality Module, Publishing Module |
| **Publish Package** | Publishing Module | Platform Adapters |
| **Performance Record** | Analytics Module | Master Orchestrator (Learning) |

### Technology Alignment

This architecture is built on the official stack defined in MASTER_CONTEXT.md:

| Concern | Technology |
|---------|------------|
| Application runtime | Python 3.14+ |
| HTTP API | FastAPI |
| Agent orchestration | LangGraph |
| Primary datastore | PostgreSQL via SQLAlchemy |
| Validation | Pydantic |
| Queue and cache | Redis |
| Media processing | FFmpeg |
| Containerization | Docker |
| Testing | Pytest |

---

## 2. Backend Modules

All modules reside within the modular monolith under `backend/`. Each module owns a bounded context with a defined public interface. Modules must not reach into each other's internal implementation. Cross-module communication occurs through orchestrator-mediated calls, shared artifact contracts (defined in `shared/`), and immutable lifecycle events.

Agent definitions, prompts, and tool configurations live in `agents/` and are invoked by their corresponding modules.

---

### API Layer

**Purpose:** The single HTTP entry point for all external interaction with the backend.

**Responsibilities:**

- Expose REST endpoints for the dashboard, automation hooks, and health checks
- Validate all inbound requests against Pydantic schemas before routing
- Authenticate and authorize every request before module delegation
- Route requests to the appropriate backend module or orchestrator
- Return consistent, typed error responses with actionable context
- Enforce rate limits and request size constraints at the edge
- Emit request-level telemetry (latency, status, caller identity)

**Boundaries:**

- Does not contain business logic belonging to domain modules
- Does not invoke AI providers or platform APIs directly
- Does not manage pipeline state — delegates to the Orchestrator

---

### Orchestrator

**Purpose:** The central nervous system of Astra. Implements the Master Orchestrator agent as a LangGraph state machine that drives the full content pipeline.

**Responsibilities:**

- Maintain pipeline state for every content job from initiation through learning
- Sequence module invocations according to the defined workflow
- Enforce stage gates — no module executes until the prior stage produces a valid artifact
- Manage human approval gates (configurable per workspace and stage)
- Handle retries, backoff, and failure escalation for transient errors
- Record immutable lifecycle events for every state transition
- Feed learning signals from Analytics back into Research configuration
- Support job cancellation, pause, and manual re-trigger of individual stages
- Coordinate concurrent pipeline executions with workspace-level quotas

**Boundaries:**

- Does not implement domain logic (script writing, video rendering, etc.)
- Does not call external platform or AI APIs directly — delegates to modules
- Owns workflow state; modules own domain artifacts

---

### Research Module

**Purpose:** Discovers raw trend signals and topic candidates from configured sources.

**Responsibilities:**

- Ingest signals from configured research sources (search trends, RSS, platform APIs, niche databases)
- Normalize raw signals into structured topic candidates
- Apply workspace-level filters (niche, language, blocklist)
- Persist research batches with timestamps and source provenance
- Hand off topic candidates to the Trend Module
- Cache recent research results in Redis to avoid redundant fetches

**Agent:** Research Agent

**Output:** Topic Candidate collection

---

### Trend Module

**Purpose:** Scores, ranks, and filters topic candidates to identify the highest-value content opportunities.

**Responsibilities:**

- Score candidates by viability, audience relevance, competition, and platform fit
- Rank topics within a research batch and against historical performance
- Apply workspace editorial rules and learning-informed weight adjustments
- Reject candidates below configurable score thresholds
- Produce a prioritized topic list for the Planning Module
- Log scoring rationale for audit and learning transparency

**Agent:** Trend Analyzer Agent

**Output:** Ranked Topic List

---

### Planning Module

**Purpose:** Converts ranked topics into actionable content briefs ready for production.

**Responsibilities:**

- Select topics from the ranked list according to editorial calendar and quotas
- Generate structured content briefs (topic, angle, hook, target platforms, tone)
- Assign platform-specific formatting hints and metadata direction
- Schedule briefs on the content calendar
- Validate brief completeness before handoff to Script Module

**Agent:** Planning Agent

**Output:** Content Brief

---

### Script Module

**Purpose:** Produces the full narrative content for a video from an approved content brief.

**Responsibilities:**

- Generate hooks, narration text, on-screen text, and call-to-action
- Draft platform metadata (title, description, hashtags, tags)
- Enforce duration and word-count constraints per platform
- Apply brand voice parameters from workspace configuration
- Produce a structured Script Package for downstream modules and quality review

**Agent:** Script Agent

**Output:** Script Package

---

### Voice Module

**Purpose:** Generates original narration audio from an approved script.

**Responsibilities:**

- Convert narration text to speech using AI voice generation
- Apply voice profile settings (tone, pace, language) from workspace config
- Produce audio files meeting platform loudness and format requirements
- Record voice provider, model, and generation parameters for provenance
- Hand off audio assets to the Video Module via the Render Manifest

**Agent:** Voice Agent

**Output:** Audio asset (referenced in Render Manifest)

---

### Visual Module

**Purpose:** Produces or sources all visual assets required for video composition.

**Responsibilities:**

- Generate AI visuals or retrieve licensed stock assets
- Record asset provenance (generated, licensed, user-uploaded) for every visual
- Enforce originality constraints — no unauthorized third-party media
- Produce assets at required resolution and aspect ratio (9:16 vertical)
- Define visual timing and layout instructions in the Render Manifest

**Agent:** Visual Agent

**Output:** Visual assets (referenced in Render Manifest)

---

### Video Module

**Purpose:** Composes visual and audio assets into a unified video file.

**Responsibilities:**

- Consume the Render Manifest to assemble visuals and narration audio
- Execute composition via FFmpeg according to timing and layout specifications
- Produce intermediate video output at target resolution and codec
- Validate technical output (duration, aspect ratio, file size, audio sync)
- Hand off composed video to the Subtitle Module

**Agent:** Video Assembly Agent

**Output:** Composed video (without subtitles)

---

### Subtitle Module

**Purpose:** Adds captions to the composed video for accessibility and platform compliance.

**Responsibilities:**

- Generate subtitle text from the approved script
- Render burned-in captions or produce platform-native caption files
- Apply subtitle styling consistent with workspace brand guidelines
- Validate caption timing against audio track
- Produce the final video file ready for quality review

**Agent:** Video Assembly Agent (subtitle mode)

**Output:** Final Video

---

### Quality Module

**Purpose:** Evaluates content at multiple pipeline stages against policy, originality, and quality rubrics.

**Responsibilities:**

- **Fact Check mode:** Verify factual claims in scripts before production begins
- **Originality validation:** Confirm content is not derived from unauthorized third-party media
- **Policy compliance:** Check against platform guidelines, workspace blocklists, and content safety rules
- **Technical validation:** Verify video specs (resolution, duration, audio levels, caption presence)
- **Brand voice evaluation:** Score alignment with workspace tone and style parameters
- Return pass/fail with detailed rubric scores and rejection reasons
- Block pipeline progression on failure; escalate to operator when configured

**Agent:** Quality Agent

**Output:** Quality Report (pass/fail with scores)

---

### Publishing Module

**Purpose:** Delivers approved content to target social platforms.

**Responsibilities:**

- Assemble the Publish Package (final video + metadata + platform overrides)
- Route to the correct platform adapter (YouTube, TikTok, Instagram)
- Execute upload and publish with idempotent retry semantics
- Capture platform post IDs for analytics correlation
- Handle scheduled vs. immediate publish modes
- Record publish events in the audit log
- Respect per-workspace daily publish caps and rate limits

**Agent:** Publishing Agent

**Output:** Publish Record (platform post ID, timestamp, status)

---

### Analytics Module

**Purpose:** Ingests platform performance data and generates learning signals.

**Responsibilities:**

- Pull metrics from platform adapters (views, engagement, retention, click-through)
- Correlate platform post IDs with internal content IDs
- Aggregate performance data into Performance Records
- Identify patterns across topics, hooks, formats, and platforms
- Generate learning signals for the Orchestrator to feed back into Research and Planning
- Support dashboard queries for operator visibility

**Agent:** Analytics Agent

**Output:** Performance Record, Learning Signals

---

## 3. AI Layer

The AI Layer is a provider-agnostic abstraction that sits between backend modules/agents and external AI services. No module or agent calls a provider API directly. All AI invocations pass through this layer.

### Abstraction Design

```
┌─────────────────────────────────────────────────────────┐
│                    AGENTS / MODULES                      │
└─────────────────────────┬───────────────────────────────┘
                          │ Task Request (typed, validated)
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   AI ABSTRACTION LAYER                   │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │    Router    │  │   Fallback   │  │  Cost Tracker │  │
│  │  (per task)  │  │    Chain     │  │  & Audit Log  │  │
│  └──────┬───────┘  └──────────────┘  └───────────────┘  │
│         │                                                │
│  ┌──────┴──────────────────────────────────────────┐    │
│  │              Provider Adapters                   │    │
│  │  OpenAI  │  Anthropic  │  Google  │  [Future]    │    │
│  └──────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────┘
                          │ Provider-specific API calls
                          ▼
                   External AI Services
```

### Layer Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **Task Router** | Selects provider and model based on task type, workspace config, cost, and latency requirements |
| **Provider Adapters** | Translate internal task requests into provider-specific API calls and normalize responses |
| **Fallback Chain** | Automatically retries with alternate providers when primary is unavailable or rate-limited |
| **Response Normalizer** | Returns structured, validated output regardless of which provider served the request |
| **Cost Tracker** | Records token usage, API calls, and spend per agent invocation and workspace |
| **Audit Logger** | Logs provider, model, prompt hash, and response metadata for every invocation |

### Supported Providers (v1.0)

| Provider | Primary Use Cases |
|----------|-------------------|
| **OpenAI** | Script generation, reasoning, embeddings, image generation |
| **Anthropic** | Long-context reasoning, fact checking, quality evaluation |
| **Google** | Multimodal generation, search grounding, alternative model routing |

### Future Providers (Post v1.0)

| Provider | Purpose |
|----------|---------|
| **Ollama** | Local model inference for development and cost-sensitive workloads |
| **vLLM** | High-throughput self-hosted inference for production scale |

Future providers integrate by implementing the same provider adapter interface. No changes to agents or modules are required when a new provider is added.

### Configuration Model

- Provider selection is **configuration-driven** per workspace and per agent task
- Each task type defines a primary provider, fallback order, and model preferences
- Provider API keys are stored encrypted in the secrets layer — never in code or version control
- Model routing decisions are logged and auditable

---

## 4. Database Layer

PostgreSQL is the system of record for all structured, relational, and audit data. SQLAlchemy serves as the ORM. Pydantic models in `shared/` define the validation contracts at module boundaries.

The database layer is responsible for the following domains. This section describes **responsibilities only** — no schema definitions.

### Workspace & Configuration

- Workspace identity, settings, and editorial rules
- Brand voice parameters, blocklists, and allowlists
- Approval gate configuration per pipeline stage
- Daily publish caps, quotas, and scheduling preferences

### Content Lifecycle

- Content job records with current pipeline stage and status
- Content Brief, Script Package, Render Manifest, and Publish Package references
- Immutable lifecycle event log (stage transitions, timestamps, actor)
- Content calendar entries and scheduling metadata

### Research & Trends

- Research batch records with source provenance
- Topic candidates and scoring results
- Historical trend data for learning-informed ranking

### Media Metadata

- Asset registry (audio, visual, video files) with storage paths and provenance
- Asset type, generation parameters, license status, and ownership
- Links between assets and content jobs

### Publishing

- Publish records with platform post IDs, timestamps, and status
- Platform credential references (encrypted tokens stored separately)
- Publish retry history and error classification

### Analytics & Learning

- Performance Records linked to content and platform post IDs
- Aggregated metrics snapshots (views, engagement, retention)
- Learning signal history and strategy adjustment records

### Audit & Compliance

- Agent decision audit trail (provider, model, inputs, outputs)
- Operator actions (approvals, rejections, configuration changes)
- Cost tracking per workspace, agent, and provider

### Identity & Access

- Operator accounts and role assignments
- Session and token metadata
- API key registry for automation access

### Data Principles

- All content lifecycle events are **immutable** once written
- Workspace-level isolation is enforced on every query
- Soft deletes for operator-facing data; hard deletes only via compliance workflows
- Migrations managed through versioned scripts in `scripts/`

---

## 5. Queue Layer

Redis serves dual roles: **job queue** for async pipeline work and **cache** for frequently accessed data.

### Job Queue Responsibilities

| Queue Domain | Purpose |
|--------------|---------|
| **Pipeline Jobs** | Async execution of long-running pipeline stages (research, render, publish) |
| **Render Jobs** | FFmpeg video composition tasks with concurrency control |
| **Publish Jobs** | Platform upload and publish with retry semantics |
| **Analytics Jobs** | Scheduled metrics ingestion from platform APIs |
| **Retry Queue** | Failed jobs awaiting exponential backoff retry |

### Queue Behavior

- Jobs are **idempotent** — safe to retry without duplicate side effects
- Priority tiers: scheduled content (normal), on-demand content (high), retry (low)
- Dead letter handling for permanently failed jobs with operator notification
- Backpressure signalled to the Orchestrator when queue depth exceeds thresholds
- Per-workspace concurrency limits enforced at enqueue time

### Cache Responsibilities

| Cache Domain | Purpose | TTL Strategy |
|--------------|---------|--------------|
| **Research Results** | Avoid redundant trend fetches | Configurable freshness window |
| **Workspace Config** | Reduce database reads for hot settings | Invalidated on config change |
| **Platform Rate Limits** | Track API call counts per platform account | Sliding window |
| **Session Data** | Operator authentication sessions | Session lifetime |
| **Provider Health** | Track provider availability for routing decisions | Short-lived, refreshed on call |

### Cache Principles

- Cache is **never the source of truth** — PostgreSQL remains authoritative
- Cache misses fall through to the database transparently
- All cache keys are workspace-scoped to prevent cross-tenant leakage

---

## 6. Storage Layer

Binary assets and log files are stored outside PostgreSQL. The storage layer handles three distinct categories.

### Assets

**Contents:** Individual media files produced or sourced during production.

| Asset Type | Examples |
|------------|----------|
| Audio | Narration tracks, background music (licensed) |
| Visual | AI-generated images, licensed stock footage, brand logos |
| Intermediate | Partial renders, preview frames |

**Responsibilities:**

- Store files organized by workspace and content job
- Record provenance metadata in PostgreSQL (storage path, type, license, generator)
- Enforce access controls — assets accessible only within their workspace context
- Apply lifecycle policies for cleanup of intermediate assets after job completion
- Support local filesystem (development) and object storage (staging/production)

### Videos

**Contents:** Composed and final video files ready for quality review and publishing.

| Video Stage | Description |
|-------------|-------------|
| Composed | Video Module output — visuals and audio merged, no subtitles |
| Final | Subtitle Module output — captions applied, ready for publish |
| Published Archive | Copy retained after successful platform upload |

**Responsibilities:**

- Store at required resolution (minimum 1080×1920) and format
- Validate file integrity on write
- Retain published video archives for compliance and re-review
- Enforce storage quotas per workspace

### Logs

**Contents:** Structured application logs, agent decision traces, and pipeline telemetry.

**Responsibilities:**

- Capture structured logs from all modules and agents
- Separate operational logs from audit logs (audit logs also persisted in PostgreSQL)
- Support log rotation and retention policies
- Enable search and filtering by workspace, content job, stage, and severity
- Never contain secrets, raw API keys, or full prompt content in production logs

### Storage Principles

- Encryption at rest for all stored media and logs in staging and production
- No binary content stored in PostgreSQL — only references and metadata
- Storage paths are opaque to external consumers; access mediated by the backend

---

## 7. External Integrations

All platform communication is isolated in dedicated adapters within `backend/`. Adapters implement a common interface; the Publishing and Analytics modules interact with platforms only through these adapters.

### Integration Architecture

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Publishing Module│     │ Analytics Module │     │  Research Module │
└────────┬─────────┘     └────────┬─────────┘     └────────┬─────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PLATFORM ADAPTER LAYER                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐   │
│  │ YouTube Adapter │ │  TikTok Adapter │ │ Instagram Adapter   │   │
│  └────────┬────────┘ └────────┬────────┘ └──────────┬──────────┘   │
└───────────┼───────────────────┼─────────────────────┼──────────────┘
            ▼                   ▼                     ▼
     YouTube Data API    TikTok Content API    Instagram Graph API
```

### Common Adapter Contract

Every platform adapter must implement:

| Capability | Description |
|------------|-------------|
| **Authentication** | OAuth token management with automatic refresh |
| **Publish** | Upload video and metadata; return platform post ID |
| **Analytics Pull** | Retrieve performance metrics for a given post ID |
| **Metadata Mapping** | Translate internal Publish Package to platform-specific schema |
| **Rate Limit Handling** | Respect platform API quotas with backoff |
| **Error Classification** | Distinguish transient failures (retry) from permanent failures (escalate) |
| **Health Check** | Report adapter connectivity and credential validity |

---

### YouTube

**Platform:** YouTube Shorts  
**API:** YouTube Data API v3

| Concern | Detail |
|---------|--------|
| **Authentication** | OAuth 2.0 with offline refresh tokens |
| **Publish** | Video upload with Shorts-eligible metadata (title, description, tags, visibility) |
| **Format** | Vertical video, ≤60 seconds, 9:16 aspect ratio |
| **Analytics** | Views, likes, comments, watch time, audience retention |
| **Rate Limits** | Quota-unit based; adapter tracks daily consumption |
| **Constraints** | Shorts shelf eligibility, community guidelines, copyright detection |

---

### TikTok

**Platform:** TikTok  
**API:** TikTok Content Posting API

| Concern | Detail |
|---------|--------|
| **Authentication** | OAuth 2.0 with token refresh |
| **Publish** | Video upload with caption, hashtags, and privacy settings |
| **Format** | Vertical video, 15–60 seconds (v1.0 focus), 9:16 aspect ratio |
| **Analytics** | Views, likes, shares, comments, average watch time |
| **Rate Limits** | Per-app and per-user limits; adapter enforces throttling |
| **Constraints** | Community guidelines, sound policy, commercial content rules |

---

### Instagram

**Platform:** Instagram Reels  
**API:** Instagram Graph API (via Meta)

| Concern | Detail |
|---------|--------|
| **Authentication** | OAuth 2.0 via Meta Business integration |
| **Publish** | Reels upload with caption, hashtags, cover frame selection |
| **Format** | Vertical video, ≤90 seconds, 9:16 aspect ratio |
| **Analytics** | Plays, likes, comments, shares, saves, reach |
| **Rate Limits** | Graph API rate limiting; adapter tracks per-account usage |
| **Constraints** | Reels-specific metadata, content policies, music licensing |

---

## 8. Dashboard

The dashboard (`frontend/`) is the operator interface for configuring, monitoring, and governing the Astra platform. It communicates exclusively with the backend via the API Layer over HTTPS.

### Communication Model

```
┌─────────────────────────┐         ┌─────────────────────────┐
│      frontend/          │  HTTPS  │   backend/ API Layer    │
│   Admin Dashboard       │ ◄─────► │       (FastAPI)         │
└─────────────────────────┘   REST  └─────────────────────────┘
```

### Dashboard Capabilities

| Capability | API Interaction |
|------------|-----------------|
| **Workspace Configuration** | CRUD workspace settings, brand voice, editorial rules, approval gates |
| **Pipeline Monitoring** | Real-time content job status, current stage, history |
| **Approval Workflow** | Review and approve/reject content at configured gates |
| **Content Calendar** | View and manage scheduled content |
| **Analytics Dashboard** | Performance metrics, trends, learning signal summaries |
| **Platform Accounts** | Connect and manage YouTube, TikTok, Instagram credentials |
| **Audit Log Viewer** | Search agent decisions, publish events, operator actions |
| **Kill Switch** | Halt all publishing for a workspace immediately |

### Communication Principles

- All requests authenticated and authorized before processing
- API responses use the same Pydantic-validated schemas defined in `shared/`
- Long-running operations (renders, publishes) return job IDs; dashboard polls for status
- WebSocket or SSE connections for real-time pipeline status updates (optional v1.0 enhancement)
- Dashboard never communicates directly with AI providers, platforms, or storage

---

## 9. Security

Security is a foundational requirement. Astra handles API credentials, autonomous publishing capability, and operator access to a content production system.

### Authentication

| Concern | Approach |
|---------|----------|
| **Operator Login** | Credential-based authentication with secure session management |
| **Session Management** | Sessions stored in Redis with configurable timeout |
| **API Access** | Scoped API keys for automation and integration access |
| **Token Format** | Signed tokens with expiration; no sensitive data in token payload |
| **Platform OAuth** | Separate OAuth flows for YouTube, TikTok, and Instagram account linking |

### Authorization

| Concern | Approach |
|---------|----------|
| **Model** | Role-Based Access Control (RBAC) |
| **Roles** | Admin, Editor, Viewer (minimum set; extensible per workspace) |
| **Scope** | All authorization checks are workspace-scoped |
| **Admin** | Full workspace configuration, credential management, kill switch |
| **Editor** | Content review, approval/rejection, calendar management |
| **Viewer** | Read-only access to pipeline status, analytics, and audit logs |
| **Agent Actions** | Agents operate under system-level service identity, not operator identity |
| **Publish Gate** | Publishing requires explicit authorization — automated or human |

### Secrets

| Secret Type | Storage | Access |
|-------------|---------|--------|
| **AI Provider API Keys** | Encrypted secrets store; never in code or version control | AI Layer only |
| **Platform OAuth Tokens** | Encrypted in PostgreSQL; auto-refresh | Platform adapters only |
| **Operator Credentials** | Hashed; never stored in plaintext | Authentication module only |
| **API Keys (automation)** | Hashed with scoped permissions | API Layer validation |
| **Encryption Keys** | Environment-injected; rotated on schedule | Infrastructure layer |

**Secrets Principles:**

- No secret appears in logs, error messages, or API responses
- Secrets templates provided in `configs/` — actual values injected at deployment
- Credential rotation supported without application downtime
- All secret access logged in the audit trail

---

## 10. Deployment

### Docker

All application components are containerized for consistent deployment across environments.

| Container | Contents |
|-----------|----------|
| **backend** | Modular monolith — FastAPI, all modules, LangGraph orchestrator |
| **frontend** | Admin dashboard static assets served via web server |
| **postgresql** | Primary datastore |
| **redis** | Queue and cache |
| **worker** | Optional dedicated container for async job processing (render, publish) |

**Container Principles:**

- Single Dockerfile per deployable unit in `docker/`
- Docker Compose for local development and staging orchestration
- Multi-stage builds for minimal production image size
- Health check endpoints on every container
- Non-root process execution in production containers
- Verified base images with dependency scanning in CI

### Environment Separation

| Environment | Purpose | Characteristics |
|-------------|---------|-----------------|
| **Local** | Developer machines | Docker Compose; mocked external APIs where feasible; local storage |
| **Development** | Shared integration environment | Real PostgreSQL and Redis; mocked platform APIs; shared AI provider keys |
| **Staging** | Pre-production validation | Production mirror; platform sandbox/test accounts; real AI providers |
| **Production** | Live operation | Full platform integrations; encrypted storage; manual deploy approval (v1.0) |

**Environment Principles:**

- Configuration via environment variables — templates in `configs/`, secrets injected at deploy
- No environment-specific code branches — behavior controlled by configuration
- Staging must mirror production topology; only credentials and scale differ
- Database migrations run as a pre-deploy step with rollback capability
- Production deploys require passing CI pipeline and manual approval gate (v1.0)

### Deployment Flow

```
Code Merge → CI Pipeline → Build Images → Deploy Staging → E2E Smoke Tests → Deploy Production
```

---

## 11. Request Flow

This section traces a complete end-to-end example: a trend is detected, content is produced, published, and the system learns from the result.

### Scenario

The Research Module detects a rising trend in "AI productivity tools." The system autonomously produces and publishes a 45-second YouTube Short, then incorporates performance data into future research.

### Flow

```
Trend Detected
      ↓
  Research
      ↓
  Planning
      ↓
   Script
      ↓
   Voice
      ↓
   Visual
      ↓
   Video
      ↓
  Quality
      ↓
  Approval
      ↓
  Publish
      ↓
 Analytics
      ↓
  Learning
```

### Step-by-Step Trace

**1. Trend Detected**

An external signal (search trend spike, RSS feed entry) is identified by the configured research source. The signal is ingested and normalized into the system.

**2. Research**

The Research Agent processes the signal. The Research Module normalizes it into a Topic Candidate ("AI productivity tools — rising search interest, low competition in Shorts format") and persists it. The candidate is enqueued for trend scoring.

**3. Planning**

The Trend Analyzer Agent scores the candidate highly for YouTube Shorts viability. The Planning Agent selects it from the ranked list and produces a Content Brief: topic angle ("3 AI tools that save 2 hours daily"), hook strategy, target platform (YouTube Shorts), tone (informative, fast-paced), and duration target (45 seconds).

**4. Script**

The Script Agent generates a Script Package: opening hook, three tool segments with narration, call-to-action, and metadata draft (title, description, tags). The Quality Module runs fact-check mode — claims about tool capabilities are verified. Script passes.

**5. Voice**

The Voice Agent generates narration audio from the approved script. Audio meets loudness and format requirements. The audio asset is registered in storage and referenced in the Render Manifest.

**6. Visual**

The Visual Agent produces visual assets: AI-generated backgrounds, text overlays for each tool name, and transitions. All assets are marked as AI-generated with provenance recorded. Visual timing and layout are defined in the Render Manifest.

**7. Video**

The Video Assembly Agent consumes the Render Manifest. FFmpeg composes visuals and narration into a 45-second vertical video (1080×1920). The Subtitle Module adds burned-in captions. The Final Video is stored and registered.

**8. Quality**

The Quality Agent evaluates the Final Video: originality (pass), policy compliance (pass), technical specs (45s, 9:16, audio levels within range — pass), brand voice alignment (score: 8.5/10 — pass). Quality Report returned with overall pass.

**9. Approval**

The Orchestrator checks the workspace approval configuration. This workspace requires human approval for first publish of a new topic category. The dashboard notifies the operator. The operator reviews the video and metadata, then approves.

**10. Publish**

The Publishing Agent assembles the Publish Package and routes to the YouTube adapter. The adapter uploads the video with title, description, and tags. YouTube returns a post ID. A Publish Record is created linking the internal content ID to the YouTube post ID.

**11. Analytics**

After the platform reporting window, the Analytics Agent pulls metrics via the YouTube adapter: 12,400 views, 6.2% engagement rate, 68% average retention. A Performance Record is created and linked to the content job.

**12. Learning**

The Orchestrator processes learning signals: "AI productivity tools" category performed above workspace average. The Trend Module's scoring weights are adjusted to favor similar topics. Future Research batches will prioritize adjacent trends ("AI workflow automation," "AI writing tools"). The learning adjustment is logged in the audit trail.

### Flow Characteristics

| Characteristic | Behavior in This Flow |
|----------------|----------------------|
| **Async execution** | Stages 2–8 run as queued jobs; operator sees progress in dashboard |
| **Artifact handoff** | Each stage produces a validated artifact before the next begins |
| **Failure handling** | Any stage failure halts the pipeline and notifies the operator |
| **Audit trail** | Every stage transition, agent decision, and operator action is logged |
| **Idempotency** | Publish step is safely retriable without duplicate uploads |

---

## 12. Architecture Principles

These principles govern all architectural decisions. They derive directly from MASTER_CONTEXT.md and must be upheld in every design and implementation choice.

### Structural Principles

| Principle | Statement |
|-----------|-----------|
| **Modular Monolith** | One deployable application with strict internal module boundaries — not microservices |
| **Service Boundaries** | Modules communicate through defined interfaces and validated artifacts, never through shared mutable state |
| **Separation of Concerns** | Each module owns one bounded context; orchestration is separate from domain logic |
| **Adapter Isolation** | All external APIs (AI providers, social platforms) accessed only through adapter layers |

### Data Principles

| Principle | Statement |
|-----------|-----------|
| **Schema-First Contracts** | All cross-module artifacts validated by Pydantic models in `shared/` |
| **Immutable Events** | Content lifecycle events are append-only and replayable |
| **Single Source of Truth** | PostgreSQL for metadata; Redis for ephemeral state; storage for binaries |
| **Provenance Tracking** | Every asset records its origin, generator, and license status |

### Operational Principles

| Principle | Statement |
|-----------|-----------|
| **Fail Safe, Not Fail Silent** | Uncertainty triggers escalation, not silent continuation |
| **Idempotent Operations** | Publish, render, and enqueue operations are safely retriable |
| **Configuration over Code** | Workspace rules, thresholds, and schedules are data-driven |
| **Observability by Default** | Every module and agent emits logs, metrics, and decision traces |
| **Graceful Degradation** | Provider outages trigger fallback chains and queue-and-retry — not data loss |

### Content Principles

| Principle | Statement |
|-----------|-----------|
| **Originality First** | All content originally produced; no copyrighted third-party reuse |
| **Platform Agnosticism** | Core logic is platform-neutral; platform specifics live in adapters |
| **Human-in-the-Loop** | Approval gates are configurable; autonomous does not mean ungoverned |
| **Cost Awareness** | Token usage, API calls, and render minutes tracked per invocation |

### Security Principles

| Principle | Statement |
|-----------|-----------|
| **Least Privilege** | Every component accesses only what it requires |
| **Defense in Depth** | Authentication, authorization, encryption, and audit at every layer |
| **Secrets Isolation** | No secrets in code, logs, or version control |
| **Workspace Isolation** | All data access scoped to workspace context |

### Evolution Principles

| Principle | Statement |
|-----------|-----------|
| **Replaceability** | Modules, providers, and adapters swappable without system rewrite |
| **Forward Compatibility** | Data models and interfaces designed for future multi-tenancy and localization |
| **Documented Decisions** | Architecture changes recorded as ADRs in `docs/adr/` |
| **Master Context Alignment** | This document and all ADRs must remain consistent with MASTER_CONTEXT.md |

---

## Appendix: Document Relationships

| Document | Role |
|----------|------|
| **MASTER_CONTEXT.md** | Single source of truth — vision, principles, scope, constraints |
| **SYSTEM_ARCHITECTURE.md** | This document — structural blueprint and module responsibilities |
| **docs/adr/** | Architecture Decision Records — specific technical choices |
| **docs/runbooks/** | Operational procedures for deployment, incident response, and recovery |

---

## Appendix: Glossary

| Term | Definition |
|------|------------|
| **Content Brief** | Structured document defining topic, angle, hook, script outline, and platform targets |
| **Render Manifest** | Machine-readable specification of all assets, timing, and composition for video assembly |
| **Publish Package** | Final deliverable bundle (video file + metadata) ready for platform upload |
| **Performance Record** | Analytics snapshot linking platform post IDs to internal content IDs |
| **Workspace** | Isolated tenant context containing config, credentials, brand rules, and content history |
| **Adapter** | Module translating between internal contracts and external platform or provider APIs |
| **Learning Loop** | Feedback cycle where analytics inform future research and creative decisions |

---

*This document describes how Astra AI Content OS is structured. Build against it. Review against it. Keep it aligned with MASTER_CONTEXT.md.*
