# FleetMind AI development plan

## Phase 0 — Foundation complete

- [x] Typed FastAPI configuration and restricted CORS
- [x] Responsive React workspace with routing
- [x] Credential-free deterministic demo mode
- [x] Amazon Bedrock Converse gateway
- [x] Cognito, DynamoDB, Lambda, HTTP API, S3, and CloudFront CDK stacks
- [x] Docker Compose local workflow
- [x] Backend, frontend, and CDK continuous integration

## Phase 1 — Functional MVP complete

- [x] Multi-assistant chat endpoint and interface
- [x] In-memory conversation history
- [x] Seeded fleet and department assistants
- [x] Fleet health dashboard
- [x] Maintenance triage agent with auditable steps
- [x] Usage and governance dashboard
- [x] Assistant builder
- [x] Validated text knowledge upload API
- [x] Signed local sessions with server-enforced manager, technician, and viewer roles
- [x] Role-aware dashboards, navigation, protected routes, and resource access
- [x] Owner-scoped conversation history and maintenance task access

## Predictive ML milestone complete

- [x] Train on the official Scania APS development split
- [x] Keep calibration, threshold selection, and official testing disjoint
- [x] Select a threshold using the published asymmetric failure costs
- [x] Publish precision, recall, ranking metrics, confusion matrix, and model limits
- [x] Run server-side inference against reproducible held-out examples
- [x] Keep fictional fleet triage visually separate from evaluated ML

## Grounded AI milestone complete

- [x] Compute fleet KPIs before LLM generation
- [x] Add deterministic composite operational-risk ranking
- [x] Publish authenticated `/api/fleet/intelligence` evidence
- [x] Inject verified fleet analytics into demo and Bedrock assistant context
- [x] Add anti-hallucination instructions for telemetry, service dates, and fleet facts
- [x] Give manager, technician, and viewer different assistant scopes
- [x] Allow viewer explanations while blocking viewer operational actions server-side
- [x] Replace hard-coded home metrics with backend-derived fleet signals
- [x] Surface grounded analytics and risk ranking in Fleet Command
- [x] Add unit and API tests for risk ranking and intelligence access

## Authentication milestone — implementation complete, deployment verification pending

- [x] Add Cognito viewer signup start/confirm API
- [x] Add email verification flow in the React login experience
- [x] Support Cognito app clients with a client secret via `SECRET_HASH`
- [x] Preserve manager and technician demo accounts while `DEMO_MODE=true`
- [x] Prevent public signup from assigning privileged roles
- [x] Configure Cognito user pool/app client and Vercel environment variables
- [ ] Complete one fresh Vercel Preview verification test after deployment quota resets
- [ ] Merge Cognito PR after real email-code verification passes

## Next domain milestone

- [ ] Compare multiple predictive-maintenance algorithms on identical, leakage-safe splits
- [ ] Select the final model using failure cost, recall, precision, and calibration evidence
- [ ] Add feature-level explanations for APS predictions
- [ ] Define an approved fleet knowledge corpus with metadata, ownership, and update rules
- [ ] Replace lexical retrieval with a production vector retrieval adapter when a free/safe deployment path is chosen
- [ ] Evaluate grounded assistant answers with a versioned question-and-evidence test set

## Phase 2 — Persistent cloud beta

- [ ] Implement DynamoDB repositories behind the store interface
- [ ] Add tenant and department partitioning
- [ ] Store approved documents in encrypted object storage
- [ ] Add production vector retrieval with role-aware metadata filters
- [ ] Stream model responses over server-sent events
- [ ] Add refresh-token/session-lifecycle handling for production Cognito users

## Phase 3 — Enterprise integrations

- [ ] Integrate a sandbox vehicle telemetry provider
- [ ] Add ServiceNow/Jira maintenance ticket connectors
- [ ] Add CRM proposal context for the sales assistant
- [ ] Add approval gates before an agent changes external systems
- [ ] Store immutable agent audit events

## Phase 4 — Reliability and governance

- [ ] Add CloudWatch dashboards, alarms, traces, and cost budgets
- [ ] Add prompt-injection and sensitive-data filters
- [ ] Evaluate RAG relevance with a versioned test dataset
- [ ] Add accessibility and browser end-to-end tests
- [ ] Add data retention, export, and deletion workflows

## Portfolio release criteria

- [x] Project starts without paid services
- [x] Every visible page has a working purpose
- [x] CI fails on test, type, or infrastructure errors
- [x] AWS architecture can be synthesized
- [x] Documentation distinguishes demo behavior from production readiness
- [x] AI answers are grounded in deterministic fleet analytics before generation
- [x] Role boundaries are enforced by the backend, not only hidden in the frontend
- [ ] Add a final interface screenshot or short demo video after deployment review
