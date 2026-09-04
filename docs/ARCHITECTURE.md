# FleetMind AI architecture

## Goals

FleetMind AI provides one internal workspace for fleet health, department
assistants, grounded answers, and maintenance automation. The design optimizes
for a convincing local demonstration while keeping clean seams for managed AWS
services.

## Runtime view

~~~mermaid
flowchart TB
    Browser["React application"]
    Gateway["CloudFront + HTTP API"]
    Service["FastAPI Lambda container"]
    Intelligence["LLM gateway + RAG + agent"]
    Predictor["Calibrated APS classifier"]
    Storage["DynamoDB + knowledge store"]

    Browser --> Gateway
    Gateway --> Service
    Service --> Intelligence
    Service --> Predictor
    Service --> Storage
~~~

In local demo mode, the browser talks directly to Uvicorn. A thread-safe
in-memory repository contains fictional vehicles, assistants, conversations,
tasks, and usage counters. Responses are deterministic, so the project works
without AWS credentials or paid model calls.

## Backend boundaries

| Module | Responsibility |
| --- | --- |
| api/routers | HTTP contracts for chat, bots, fleet, agents, auth, and admin |
| core | Typed environment configuration and authentication boundary |
| services/store.py | Local repository and demo seed data |
| services/llm_gateway.py | Demo response strategy and Bedrock Converse call |
| rag | Validated text ingestion, chunking, and retrieval |
| agents | Multi-step maintenance workflow and external connector boundary |
| ml | Trusted model loading, model card, and held-out sample inference |
| models | Shared Pydantic request and response contracts |

The API does not expose Python exceptions or provider details to clients.
Knowledge uploads accept only small UTF-8 text formats in the MVP.

## Main request flows

### Grounded chat

~~~mermaid
sequenceDiagram
    participant U as User
    participant A as Chat API
    participant R as Retriever
    participant L as LLM gateway
    U->>A: Message and assistant ID
    A->>R: Retrieve matching knowledge
    R-->>A: Ranked snippets
    A->>L: Prompt, policy, and context
    L-->>A: Answer
    A-->>U: Answer and source IDs
~~~

### Maintenance triage

~~~mermaid
sequenceDiagram
    participant U as Fleet operator
    participant A as Agent API
    participant T as Telemetry connector
    participant M as Ticket connector
    U->>A: Triage vehicle
    A->>T: Read health signal
    T-->>A: Demo telemetry
    opt Risk threshold reached
        A->>M: Create maintenance ticket
        M-->>A: Ticket ID
    end
    A-->>U: Steps, decision, and output
~~~

The connector functions are deterministic adapters. Real telemetry and
ticketing integrations can replace them without changing the API contract.

### Predictive-maintenance inference

The APS classifier is trained offline by a reproducible script. The runtime
loads a versioned repository-owned artifact and accepts only bundled held-out
sample identifiers; clients cannot provide a path to an arbitrary serialized
model. The API returns its score, selected threshold, prediction, actual test
label, and model version. Dataset provenance and full evaluation metrics are
available through the same API.

This path is intentionally separate from Fleet overview. Those five vehicles
have readable but fictional dashboard fields, while the official Scania model
requires 170 anonymized sensor features.

## Frontend

The frontend uses React and TypeScript with a shared application shell:

- AI Workspace for assistant selection and chat;
- Fleet overview for operational KPIs and maintenance triage;
- AI Marketplace for approved department assistants;
- Bot Builder for creating an assistant definition;
- Usage & Admin for adoption and governance signals.
- Predictive ML for dataset provenance, held-out metrics, and sample inference.

The layout is responsive and uses relative /api calls by default. Vite proxies
those calls during local development; CloudFront routes them to API Gateway in
AWS.

## AWS stacks

| Stack | Resources |
| --- | --- |
| FleetMindAuthStack | Cognito user pool, web client, and manager/technician/viewer groups |
| FleetMindDataStack | On-demand conversations, bots, and tasks tables |
| FleetMindApiStack | Lambda container, HTTP API, logs, and Bedrock IAM policy |
| FleetMindFrontendStack | Private S3 bucket, origin access control, CloudFront |

The demo API Gateway route has no managed authorizer, but FastAPI still requires
the signed session issued by the local login endpoint. The production context
adds the Cognito JWT authorizer and selects Bedrock. The frontend Cognito login
experience remains a milestone before production mode is used.

## Security model

- No AWS key, password, token, or real operational data belongs in Git.
- Local demo authentication issues expiring HMAC-signed bearer sessions after server-side credential checks.
- FastAPI enforces manager, technician, and viewer permissions on routes and assistant resources.
- Conversation histories are owner-scoped, and technicians cannot access manager or sales assistants.
- Production requests are accepted only after API Gateway validates Cognito JWTs.
- Backend identity is read from API Gateway authorizer claims, not an unverified token.
- CloudFront serves the web bucket privately and proxies API calls on one origin.
- DynamoDB point-in-time recovery and resource retention are enabled in production.
- AI recommendations remain advisory for safety-critical maintenance.

## Persistence path

The current repository is intentionally replaceable:

1. implement DynamoDB repositories behind the store interface;
2. add tenant and department keys to every record;
3. add a managed vector index or Bedrock Knowledge Base;
4. encrypt tenant documents and define retention/deletion jobs;
5. add CloudWatch metrics, traces, alarms, and audit events.

## Known MVP limits

- Data resets when the local backend process restarts.
- Retrieval is lexical, not embedding-based.
- Chat is request/response rather than streamed.
- Connectors do not call real fleet, CRM, ERP, or ticketing systems.
- Cognito resources exist, but the React login flow is not yet implemented.
- The APS model has historical held-out evidence but no live-fleet validation.
