# FleetMind AI development plan

## Phase 0 — Foundation complete

- [x] Typed FastAPI configuration and restricted CORS
- [x] Responsive React workspace with routing
- [x] Credential-free deterministic demo mode
- [x] Amazon Bedrock Converse gateway
- [x] AWS CDK path for Cognito, DynamoDB, Lambda, HTTP API, S3, and CloudFront
- [x] Docker Compose local workflow
- [x] Backend, frontend, and CDK continuous integration

## Phase 1 — Functional product complete

- [x] Multi-assistant chat endpoint and interface
- [x] In-memory conversation history
- [x] Seeded role assistants
- [x] Fleet health dashboard
- [x] Maintenance triage agent with auditable steps
- [x] Usage and governance dashboard
- [x] Assistant builder and validated knowledge upload
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
- [x] Explain score, decision threshold, threshold distance, confirmed outcome, and action scope
- [x] Avoid invented physical feature meanings because the APS inputs are anonymized

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
- [x] Support direct vehicle-ID questions with verified vehicle facts
- [x] Add unit and API tests for risk ranking and intelligence access

## AI cloud architecture milestone complete

- [x] Add configurable local / Bedrock Knowledge Bases retrieval boundary
- [x] Add assistant-aware retrieval filtering
- [x] Preserve a safe local RAG fallback
- [x] Add optional Bedrock Converse generation path
- [x] Add optional Bedrock Guardrails configuration
- [x] Add DynamoDB persistence adapters for conversations, assistants, and agent tasks
- [x] Add structured audit events suitable for CloudWatch Lambda logs
- [x] Wire AWS IAM/CDK paths for optional Bedrock services
- [x] Keep metered generative AI opt-in rather than required

## AWS free-tier-safe milestone complete

- [x] Add `AWS_FREE_TIER_ONLY=true` as the default runtime cost guard
- [x] Force effective LLM provider to credential-free demo mode while safe mode is enabled
- [x] Force effective RAG provider to the local approved corpus while safe mode is enabled
- [x] Block Bedrock model, Knowledge Base, and Guardrail execution in safe mode
- [x] Omit Bedrock IAM permissions from the safe CDK stack
- [x] Reduce Lambda memory and log retention for the demo stack
- [x] Keep DynamoDB persistence available
- [x] Expose effective provider / cost-guard state in manager readiness
- [x] Add regression tests preventing accidental metered Bedrock calls
- [x] Add explicit `synth:free`, `diff:free`, and `deploy:free` commands
- [x] Document the free-tier-safe deployment and teardown procedure

## Governance and observability milestone complete

- [x] Add manager-only usage analytics
- [x] Add manager-only `/api/admin/readiness` runtime evidence
- [x] Report effective LLM/RAG provider, grounding path, predictive artifact state, persistence mode, and environment
- [x] Verify the bundled model artifact hash before inference
- [x] Surface runtime evidence in the governance UI
- [x] Keep secrets out of runtime-status responses
- [x] Emit structured assistant and agent audit events

## Optional cloud authentication path

- [x] Cognito viewer signup and email-verification implementation exists
- [x] Role-escalation protections exist for public signup
- [x] Client-secret support exists through `SECRET_HASH`
- [ ] Final live Cognito verification is optional and not a portfolio-release blocker

## Portfolio release — code complete

- [x] Project starts without paid AI services
- [x] Every visible page has a working purpose
- [x] CI fails on test, type, or infrastructure errors
- [x] AWS architecture can be synthesized in free-tier-safe mode
- [x] Documentation distinguishes demo behavior from production readiness
- [x] AI answers are grounded before generation
- [x] Role boundaries are enforced at the API boundary
- [x] Predictive ML is evaluated on a real held-out dataset
- [x] Model uncertainty and scope are visible to the user
- [x] Governance exposes runtime evidence rather than static claims
- [x] Owner-only deployment actions are isolated in `docs/USER_ACTIONS_LAST.md`

## Final owner-side validation — intentionally deferred

These steps require access to the owner's AWS account and are the only remaining actions before measuring the real live limits:

- [ ] Confirm current AWS Free plan / Free Tier allowances in the account
- [ ] Authenticate AWS CLI for the intended account/region
- [ ] Bootstrap CDK if needed
- [ ] Run `npm run diff:free`
- [ ] Run `npm run deploy:free`
- [ ] Execute the live smoke-test checklist
- [ ] Inspect Billing / Free Tier usage after deployment
- [ ] Record real latency, persistence, concurrency, and usage limits from the live environment

See `docs/AWS_FREE_TIER_DEPLOYMENT.md` and `docs/USER_ACTIONS_LAST.md`.

## Future enterprise extensions — intentionally out of portfolio scope

These are not required to call the portfolio project complete. They are realistic production extensions:

- tenant partitioning and enterprise data lifecycle policies;
- always-on production vector retrieval / Bedrock Knowledge Bases;
- encrypted enterprise document ingestion pipelines;
- real or sandbox vehicle telemetry integration;
- ServiceNow/Jira ticket connectors with approval gates;
- immutable external audit storage;
- CloudWatch dashboards, tracing, budgets, and alerts;
- versioned RAG evaluation and browser end-to-end tests;
- retention, export, deletion, and enterprise compliance workflows.
