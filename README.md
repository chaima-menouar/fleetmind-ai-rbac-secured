# FleetMind AI

FleetMind AI is a role-aware AI and cloud fleet-operations platform built as a portfolio-grade engineering project. It combines deterministic fleet analytics, grounded AI assistants, predictive maintenance ML, secure role-based access, and an AWS deployment path in one responsive workspace.

The project is deliberately explicit about data boundaries: fictional fleet telemetry is never presented as real vehicle data, while the predictive-maintenance classifier is trained and evaluated separately on the official Scania APS dataset.

## Why FleetMind is different

FleetMind does not ask an LLM to invent operational KPIs. The response path is:

**fleet data → deterministic analytics → retrieved knowledge → role policy → LLM explanation**

This keeps vehicle facts, risk scores, and service urgency grounded before a generative model is allowed to explain or prioritize them.

## Core capabilities

| Capability | Implementation |
| --- | --- |
| Grounded fleet intelligence | Deterministic KPI and composite risk scoring before the LLM layer |
| Role-scoped AI | Manager, technician, and viewer assistants with server-enforced access |
| RAG foundation | Validated text ingestion, chunking, retrieval, and cited knowledge context |
| Fleet command | Health, battery, location, service urgency, and ranked operational risk |
| Maintenance agent | Telemetry lookup, deterministic triage, and auditable mock ticket creation |
| Predictive ML | Reproducible Scania APS classifier with held-out metrics and live sample inference |
| Authentication | Signed demo sessions plus Cognito viewer email-verification integration |
| RBAC security | Manager, technician, and viewer permissions enforced at API boundaries |
| Governance | Manager-only usage analytics, upload restrictions, CORS controls, and data-boundary notices |
| Cloud path | Amazon Cognito, Bedrock integration, DynamoDB, Lambda, API Gateway, S3, CloudFront, and CDK |
| CI | Backend lint/type/tests, frontend build, and infrastructure validation in GitHub Actions |

## Architecture

~~~mermaid
flowchart LR
    Web["React + TypeScript workspace"] --> API["FastAPI service"]
    API --> Auth["RBAC + Cognito"]
    API --> Analytics["Deterministic fleet analytics"]
    Analytics --> Agent["Role policy + agent orchestration"]
    Agent --> RAG["Retrieved approved knowledge"]
    RAG --> LLM["Demo gateway / Amazon Bedrock"]
    API --> ML["Scania APS classifier"]
    API --> Data["Demo store / DynamoDB path"]
~~~

### AI grounding path

1. The backend reads authenticated fleet data.
2. FleetMind computes KPIs and composite risk scores deterministically.
3. The current role selects exactly one approved assistant scope.
4. Retrieved knowledge and verified fleet analytics are injected into the model context.
5. The LLM explains evidence; it does not calculate or fabricate telemetry.
6. Operational actions remain protected by RBAC even if the UI is bypassed.

## Role model

| Role | Assistant | Main access |
| --- | --- | --- |
| Fleet manager | Manager Intelligence | Fleet KPIs, operational priorities, governance, assistant management |
| Technician | Technician Assistant | Maintenance diagnostics, triage, predictive ML, approved technical knowledge |
| Viewer | Viewer Assistant | Read-only fleet status and explanations; no operational writes |

Self-registered Cognito users are treated as viewers. Public signup is not allowed to write privileged role or department attributes.

## Quick start with Docker

Prerequisites: Docker Desktop and Docker Compose.

~~~bash
docker compose up --build
~~~

Open:

- Web app: <http://localhost:5173>
- API documentation: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

Demo accounts:

| Role | Email | Password |
| --- | --- | --- |
| Fleet manager | manager@fleetmind.demo | FleetMind2026! |
| Technician | technician@fleetmind.demo | Service2026! |
| Viewer | viewer@fleetmind.demo | View2026! |

These credentials and the fleet records are fictional demonstration data only.

## Main product workflows

1. Sign in with a role-scoped account.
2. Open **Fleet Command** to inspect grounded KPIs and operational risk ranking.
3. Ask **My Assistant** a natural-language question; only the assistant allowed for the current role is exposed.
4. As manager or technician, run maintenance triage for an approved vehicle.
5. Open **Predictive ML** to inspect the Scania APS model card, held-out metrics, threshold, limitations, and live sample inference.
6. As manager, inspect governance and usage analytics.

## Predictive-maintenance model

The bundled model is a calibrated histogram gradient boosting classifier trained from the official UCI **APS Failure at Scania Trucks** dataset.

Held-out evaluation on 16,000 rows reports approximately:

- recall: 93.07%
- precision: 53.94%
- asymmetric cost reduction: 91.48% versus an all-negative baseline

The model uses 170 anonymized features and predicts APS-related failure only. It does **not** score the fictional vehicles displayed in Fleet Command, and it is not validated for safety-critical production decisions.

See `docs/MODEL_CARD.md` for methodology and limitations.

## Amazon Cognito

The backend supports real viewer signup and email verification through Amazon Cognito while keeping manager and technician demo accounts available when `DEMO_MODE=true`.

Expected deployment variables:

~~~env
AWS_REGION=eu-north-1
COGNITO_CLIENT_ID=<app-client-id>
COGNITO_CLIENT_SECRET=<app-client-secret-if-configured>
DEMO_MODE=true
DEMO_AUTH_SECRET=<strong-random-secret>
~~~

Cognito requirements:

- self-registration enabled;
- email verification enabled;
- username/password authentication enabled;
- email and name writable;
- public app clients must not be allowed to write privileged role or department attributes.

Do not commit Cognito secrets or AWS credentials.

## Amazon Bedrock

FleetMind can use a deterministic credential-free demo gateway or Amazon Bedrock.

Demo:

~~~env
LLM_PROVIDER=demo
~~~

Bedrock:

~~~env
LLM_PROVIDER=bedrock
AWS_REGION=<supported-region>
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
~~~

When Bedrock is enabled, FleetMind injects verified fleet analytics and retrieved knowledge into the prompt before generation. AWS credentials use the normal SDK credential chain and must never be committed.

## API surface

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Service status |
| POST | `/api/auth/login` | Demo/Cognito sign-in |
| POST | `/api/auth/register-viewer/start` | Start Cognito viewer signup and email verification |
| POST | `/api/auth/register-viewer/confirm` | Confirm viewer verification code |
| GET | `/api/auth/me` | Current authenticated user |
| GET | `/api/fleet/summary` | Fleet health overview |
| GET | `/api/fleet/intelligence` | Deterministic KPIs and operational risk ranking |
| POST | `/api/chat/message` | Role-scoped grounded assistant message |
| GET | `/api/chat/history/{id}` | Read owned conversation history |
| GET | `/api/bots` | List assistants allowed for current role |
| POST | `/api/bots` | Manager-only assistant creation |
| POST | `/api/bots/{id}/knowledge` | Manager-only validated knowledge upload |
| POST | `/api/agents/run` | Manager/technician maintenance triage |
| GET | `/api/admin/usage` | Manager-only workspace usage |
| GET | `/api/ml/model-card` | Model dataset, training, metrics, and limitations |
| GET | `/api/ml/samples` | Operator-only held-out sample list |
| POST | `/api/ml/predict` | Operator-only APS sample inference |

## Repository layout

~~~text
fleetmind-ai-rbac-secured/
├── backend/             FastAPI, auth, RBAC, analytics, RAG, agents, ML, tests
├── frontend/            React + TypeScript role-aware workspace
├── cdk/                 AWS infrastructure as code
├── examples/            Assistant configs and sample knowledge
├── docs/                Architecture, API guide, model card, roadmap
├── compose.yaml         Local multi-service demo
├── vercel.json          Vercel services routing
└── .github/workflows/   Backend, frontend, and infrastructure CI
~~~

## Quality checks

~~~bash
cd backend
poetry run ruff check app tests scripts
poetry run mypy app
poetry run pytest

cd ../frontend
npm run build

cd ../cdk
npm run build
npm run synth
~~~

CI runs these checks without ignoring failures.

## Current scope and production boundary

FleetMind is a portfolio engineering platform, not a production fleet-control system. The current fleet telemetry and people are fictional. Demo state is in-memory. Cognito viewer authentication, AWS infrastructure, DynamoDB adapters, Bedrock, and other cloud components are designed as deployable integration paths, but a real fleet would still require validated telemetry ingestion, persistent production adapters, observability, secrets management, load testing, domain validation, and safety review.

The project intentionally separates three concerns:

- **deterministic operational analytics** for verifiable fleet facts;
- **machine learning** for the independently evaluated Scania APS failure task;
- **generative AI** for role-scoped explanation and decision support.

## Author

Developed and maintained by **Chaima Menouar**.
