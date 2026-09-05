# FleetMind AI Cloud architecture

FleetMind keeps the portfolio demo usable without paid cloud services while exposing a production-ready AWS integration path.

## Request path

1. React sends an authenticated request to FastAPI.
2. Backend RBAC selects the assistant allowed for the current role.
3. Deterministic fleet analytics compute KPIs and operational risk before generation.
4. RAG retrieves approved context from the local corpus or Amazon Bedrock Knowledge Bases.
5. Fleet facts plus retrieved evidence are injected into the LLM context.
6. Amazon Bedrock Converse generates the explanation when `LLM_PROVIDER=bedrock`.
7. An optional existing Bedrock Guardrail can be applied to every Bedrock generation.
8. Conversation messages, user-created assistants, and agent tasks persist to DynamoDB when the table variables are configured.
9. Structured audit events are written as JSON logs; Lambda deployments send these logs to CloudWatch automatically.

## AI safety boundaries

- fleet KPIs and risk scores are computed deterministically, not invented by the LLM;
- role authorization is enforced by backend APIs;
- RAG filters cloud retrieval by `assistant_id` metadata;
- Bedrock Knowledge Bases are optional and have a safe local fallback;
- Bedrock Guardrails are optional and disabled unless explicitly configured;
- audit events store identifiers and outcome metadata, not user message bodies;
- the Scania APS predictive model remains separate from fictional FleetMind vehicle telemetry.

## Retrieval configuration

```env
RAG_PROVIDER=local
RAG_TOP_K=5
BEDROCK_KNOWLEDGE_BASE_ID=
```

For Bedrock Knowledge Bases:

```env
RAG_PROVIDER=bedrock_kb
BEDROCK_KNOWLEDGE_BASE_ID=<knowledge-base-id>
RAG_TOP_K=5
```

Documents indexed in the knowledge base should include an `assistant_id` metadata field matching the FleetMind assistant id, for example `technician`, `fleet-manager`, or `viewer-assistant`.

## Bedrock generation

```env
LLM_PROVIDER=bedrock
AWS_REGION=<bedrock-region>
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
```

The Lambda execution role includes permissions for model invocation and Bedrock retrieval. Keep AWS credentials outside the repository and use the normal SDK credential chain or the Lambda execution role.

## Optional Bedrock Guardrails

FleetMind can apply an already-created Bedrock Guardrail without changing application code:

```env
BEDROCK_GUARDRAIL_ID=<guardrail-id>
BEDROCK_GUARDRAIL_VERSION=DRAFT
```

When no guardrail id is configured, the application does not send `guardrailConfig` to Bedrock.

## Persistence

The CDK stack provisions DynamoDB tables for conversations, assistants, and agent tasks. The backend switches to these adapters when the corresponding environment variables are present:

```env
CONVERSATIONS_TABLE=<table-name>
BOTS_TABLE=<table-name>
TASKS_TABLE=<table-name>
```

Local development continues to use the thread-safe in-memory store.

## Observability

The API emits structured JSON audit events for assistant requests and maintenance-agent runs. On AWS Lambda these events flow into the function log group in CloudWatch. Events contain operational identifiers and outcome metadata, not prompt or response bodies.

The manager readiness endpoint exposes non-secret runtime evidence including LLM provider, RAG provider, retrieval mode, guardrail state, predictive artifact state, and persistence mode.

## Production extensions

A real enterprise rollout would additionally require validated telemetry ingestion, managed secret rotation, alarms and budgets, load testing, retention policies, RAG evaluation datasets, incident response, and domain/safety validation. These are deployment and operations requirements rather than hidden capabilities of the portfolio demo.
