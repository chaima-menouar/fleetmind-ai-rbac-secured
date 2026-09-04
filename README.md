# FleetMind AI

FleetMind AI is a functional enterprise fleet-operations MVP. It combines
department-specific AI assistants, lightweight retrieval, fleet health data,
an auditable maintenance agent, and a reproducible predictive-maintenance model
in one responsive workspace.

The repository runs without cloud credentials in **demo mode**. Amazon Bedrock
and AWS infrastructure are optional deployment paths, not requirements for the
local demo.

## What works

| Capability | MVP implementation |
| --- | --- |
| AI workspace | Multi-assistant chat with conversation history and cited knowledge sources |
| Modern interface | Responsive glass UI, gradient identity, custom SVG icons, and accessible motion |
| Assistant marketplace | Three seeded assistants plus creation of new assistants |
| RAG foundation | Safe UTF-8 text ingestion, chunking, and local keyword retrieval |
| Fleet command | Health, battery, service urgency, and status for demo vehicles |
| Maintenance agent | Telemetry lookup, risk decision, and mock ticket creation |
| Predictive ML | Trained Scania APS classifier, held-out metrics, model card, and live sample inference |
| Role security | Signed demo sessions plus server-enforced manager, technician, and viewer permissions |
| Governance | Manager-only usage analytics, upload limits, restricted CORS, and demo-data boundary |
| Cloud infrastructure | Cognito, DynamoDB, Lambda container, HTTP API, S3, and CloudFront |

## Architecture

~~~mermaid
flowchart LR
    Web["React workspace"] --> API["FastAPI service"]
    API --> AI["LLM + RAG layer"]
    API --> Data["Fleet and app data"]
    API --> ML["Trained APS classifier"]
    AI --> Bedrock["Amazon Bedrock"]
~~~

- **Local mode:** deterministic AI responses and in-memory sample data.
- **AWS demo mode:** the same API runs as a Lambda container behind API Gateway.
- **Production boundary:** Cognito can protect the API, while DynamoDB tables are
  provisioned for persistent adapters.

See [Architecture](docs/ARCHITECTURE.md) for the detailed decisions,
[APS model card](docs/MODEL_CARD.md) for evaluation evidence, and
[Development plan](docs/PLAN.md) for the next milestones.

## Quick start with Docker

Prerequisites: Docker Desktop and Docker Compose.

~~~bash
docker compose up --build
~~~

Open:

- Web app: <http://localhost:5173>
- API documentation: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

Local test accounts:

| Role | Email | Password | Access |
| --- | --- | --- | --- |
| Fleet manager | manager@fleetmind.demo | FleetMind2026! | Full workspace, assistant management, and governance |
| Technician | technician@fleetmind.demo | Service2026! | Fleet operations, maintenance AI, and approved technical assistants |
| Viewer | viewer@fleetmind.demo | View2026! | Read-only overview and vehicle status |

These credentials contain fictional demo data only. Override them through the
backend environment before sharing a deployed demonstration.

Stop the project with Ctrl+C, then:

~~~bash
docker compose down
~~~

## Manual local setup

Prerequisites:

- Python 3.12 and Poetry
- Node.js 24 and npm

Backend:

~~~bash
cd backend
cp .env.example .env
poetry install
poetry run uvicorn app.main:app --reload
~~~

Frontend, in a second terminal:

~~~bash
cd frontend
cp .env.example .env
npm install
npm run dev
~~~

The Vite development server proxies /api to the backend. The explicit
VITE_API_BASE_URL value is useful when the services run on different hosts.

## Try the main workflows

1. Open **AI Workspace** and ask the technician assistant about a battery alert.
2. Open **Fleet overview** and run triage for vehicle FM-4410.
3. Open **Predictive ML**, inspect held-out metrics, and score an official test sample.
4. Open **AI marketplace** to compare the seeded assistants.
5. Open **Build an assistant** and create a new department copilot.
6. Open **Usage & admin** to see session activity.

The navigation and dashboard change with the signed-in role. Hiding a menu item
is not the security boundary: protected API endpoints independently return 403
when the role is not allowed.

Displayed people, fleet vehicles, dashboard telemetry, and tickets are fictional
demo data. Predictive ML is separate: it runs a real trained model against
examples taken from the official held-out Scania APS test split.

## Predictive-maintenance model

The bundled model is a calibrated histogram gradient boosting classifier trained
from the official UCI **APS Failure at Scania Trucks** dataset. Its 16,000-row
held-out evaluation achieved 93.07% recall, 53.94% precision, and a 91.48%
reduction in the dataset's asymmetric error cost versus an all-negative baseline.

The model uses 170 anonymized features and predicts APS-related failure only. It
does not score the fictional vehicles on the Fleet overview page and must not be
used for safety decisions. Full methodology and limitations are in the
[model card](docs/MODEL_CARD.md).

## Amazon Bedrock

The default provider is deterministic and credential-free:

~~~env
DEMO_MODE=true
LLM_PROVIDER=demo
~~~

To use Bedrock locally, configure an AWS identity with permission to invoke the
selected model, then change:

~~~env
DEMO_MODE=true
LLM_PROVIDER=bedrock
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
~~~

Do not commit AWS keys. The SDK uses the normal AWS credential chain.

## AWS CDK

The CDK application creates:

- a Cognito user pool and web client;
- DynamoDB tables for conversations, assistants, and agent tasks;
- a container-image Lambda and HTTP API;
- a private S3 web bucket and CloudFront distribution;
- a CloudFront /api/* route to avoid cross-origin calls.

Build the web asset before synthesizing:

~~~bash
cd frontend
npm ci
npm run build

cd ../cdk
npm ci
npm run build
npm run synth
~~~

After aws configure and cdk bootstrap, deploy the credential-free AWS demo:

~~~bash
npm run deploy
~~~

The production=true context enables the Cognito authorizer and Bedrock. Do not
enable it until a Cognito login flow is added to the frontend:

~~~bash
npx cdk deploy --all -c production=true
~~~

AWS resources can generate charges. Review cdk diff before every deployment
and destroy demo stacks when they are no longer needed.

## API surface

| Method | Path | Purpose |
| --- | --- | --- |
| GET | /health | Service status |
| POST | /api/auth/login | Create a signed local demo session |
| POST | /api/auth/register-viewer | Create a read-only local viewer |
| GET | /api/auth/me | Current demo/Cognito user |
| POST | /api/chat/message | Send a message through RAG and the LLM gateway |
| GET | /api/chat/history/{id} | Read a conversation |
| GET/POST | /api/bots | List or create assistants |
| POST | /api/bots/{id}/knowledge | Add a validated text source |
| GET | /api/fleet/summary | Fleet health overview |
| POST | /api/agents/run | Run maintenance triage |
| GET | /api/admin/usage | Workspace usage summary |
| GET | /api/ml/model-card | Read dataset, training, metrics, and limits |
| GET | /api/ml/samples | List bundled held-out examples |
| POST | /api/ml/predict | Score a bundled example with the trained model |

Request examples are documented in [API guide](docs/API.md).

## Repository layout

~~~text
fleetmind-ai/
├── backend/             FastAPI, RAG, agent, trained model, and tests
├── frontend/            React + TypeScript workspace
├── cdk/                 AWS infrastructure as code
├── examples/            Importable bot configs and sample knowledge
├── docs/                Architecture, API guide, and roadmap
├── compose.yaml         One-command local demo
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

CI runs the same checks without ignoring failures.

## Current scope

This is a portfolio MVP, not a production fleet-control system. Local viewer
accounts, data, and conversations reset when the backend restarts. The trained
model is evaluated honestly on historical data but is not validated for a live
fleet. DynamoDB adapters, vector search, Cognito UI, streaming chat, and real
telemetry/CRM integrations remain planned work.

## Author

Developed and maintained by **Chaima Menouar**.
#   f l e e t m i n d - a i - r b a c - s e c u r e d  
 