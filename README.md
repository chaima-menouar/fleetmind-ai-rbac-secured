# FleetMind AI

FleetMind AI is a role-aware AI and cloud fleet-operations platform built as a portfolio-grade engineering project. It combines deterministic fleet analytics, grounded AI assistants, predictive maintenance ML, secure role-based access, governance evidence, and an AWS deployment path in one responsive workspace.

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
| Model explainability | Score, threshold distance, confirmed outcome, action scope, and explicit anonymized-feature limits |
| RBAC security | Manager, technician, and viewer permissions enforced at API boundaries |
| Governance | Manager-only usage analytics plus runtime readiness evidence |
| Cloud path | Amazon Bedrock, Cognito, DynamoDB, Lambda, API Gateway, S3, CloudFront, and CDK |
| CI | Backend lint/type/tests, frontend build, and infrastructure validation in GitHub Actions |

## Architecture

~~~mermaid
flowchart LR
    Web["React + TypeScript workspace"] --> API["FastAPI service"]
    API --> Auth["RBAC / optional Cognito"]
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
5. Open **Predictive ML** to inspect the Scania APS model card, held-out metrics, threshold, score distance, limitations, and live sample inference.
6. As manager, inspect usage analytics and runtime-readiness evidence in **Governance**.

## Predictive-maintenance model

The bundled model is a calibrated histogram gradient boosting classifier trained from the official UCI **APS Failure at Scania Trucks** dataset.

Held-out evaluation on 16,000 rows reports approximately:

- recall: 93.07%
- precision: 53.94%
- asymmetric cost reduction: 91.48% versus an all-negative baseline

The model uses 170 anonymized features and predicts APS-related failure only. It does **not** score the fictional vehicles displayed in Fleet Command, and it is not validated for safety-critical production decisions.

Because the original APS features are anonymized, FleetMind intentionally does not invent physical sensor meanings. The UI explains score, decision threshold, distance from threshold, confirmed outcome, and action scope instead.

See `docs/MODEL_CARD.md` for methodology and limitations.

## Governance and readiness

The manager-only governance area combines usage analytics with runtime evidence from:

`GET /api/admin/readiness`

It reports non-secret deployment facts including:

- current environment and LLM provider;
- grounding architecture;
- predictive-model artifact state and version;
- persistence mode;
- authentication capability;
- configured CORS-origin count.

The bundled predictive artifact is hash-verified before inference.

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

## Optional Cognito path

The repository contains a Cognito viewer signup and email-verification integration, including protection against self-assigned privileged roles. It is an optional cloud-authentication path and is not required for the portfolio release.

Do not commit Cognito secrets or AWS credentials.

## API surface

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Service status |
| POST | `/api/auth/login` | Demo/Cognito sign-in |
| POST | `/api/auth/register-viewer/start` | Optional Cognito viewer signup start |
| POST | `/api/auth/register-viewer/confirm` | Optional Cognito verification confirm |
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
| GET | `/api/admin/readiness` | Manager-only runtime evidence |
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
├── docs/                Architecture, API guide, model card, release notes
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

## Portfolio release status

The repository is complete for portfolio use. The release demonstrates AI engineering, machine learning, cloud architecture, security, backend/frontend development, and MLOps-quality evidence without pretending to be a production fleet-control system.

Real fleet deployment would still require validated telemetry ingestion, persistent enterprise adapters, production observability, secrets management, load testing, domain validation, and safety review. Those are future enterprise extensions rather than missing portfolio features.

See `docs/FINAL_RELEASE.md` for the final release boundary.

## Author

Developed and maintained by **Chaima Menouar**.
