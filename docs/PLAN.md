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

## Next domain milestone

- [ ] Compare multiple predictive-maintenance algorithms on identical, leakage-safe splits
- [ ] Select the final model using failure cost, recall, precision, and calibration evidence
- [ ] Add feature-level explanations and map every prediction to a vehicle and recommendation
- [ ] Define the approved fleet knowledge corpus, metadata, ownership, and update process
- [ ] Replace lexical retrieval with Amazon Bedrock Knowledge Bases and role-aware metadata filters
- [ ] Feed authorized vehicle and predictive-maintenance results into grounded assistant responses

## Phase 2 — Persistent cloud beta

- [ ] Implement DynamoDB repositories behind the store interface
- [ ] Add tenant and department partitioning
- [ ] Add Bedrock Knowledge Bases or OpenSearch vector retrieval
- [ ] Store documents in an encrypted S3 bucket
- [ ] Stream model responses over server-sent events
- [ ] Add Cognito login, logout, and refresh to the existing role-aware navigation

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
- [ ] Add an interface screenshot or short demo video after local review
