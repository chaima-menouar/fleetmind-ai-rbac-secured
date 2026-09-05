# AWS free-tier-safe deployment

This is the deployment path to use for the portfolio demo when the goal is to avoid activating metered generative-AI services.

## What the safe mode does

`AWS_FREE_TIER_ONLY=true` is the runtime guard. In this mode FleetMind:

- uses the deterministic demo LLM path;
- uses the local approved RAG corpus;
- does not call Amazon Bedrock model inference;
- does not call Bedrock Knowledge Bases;
- does not apply Bedrock Guardrails;
- keeps DynamoDB persistence available when tables are configured;
- keeps the predictive Scania APS model running from the bundled artifact;
- exposes effective providers and the cost guard in manager readiness.

The CDK application also defaults to `freeTierOnly=true`. The safe stack omits Bedrock IAM permissions, uses a smaller Lambda memory size, and keeps log retention short.

## Pre-deployment checks

From the repository root:

```bash
cd frontend
npm ci
npm run build

cd ../backend
poetry install
poetry run ruff check .
poetry run mypy app
poetry run pytest

cd ../cdk
npm ci
npm run build
npm run synth:free
```

All checks should pass before touching the AWS account.

## Owner-side AWS steps

These steps require access to the AWS account and are intentionally left to the repository owner:

```bash
aws sts get-caller-identity
aws configure get region
```

Set the intended region if needed, then bootstrap CDK once for that account/region:

```bash
npx cdk bootstrap
```

Review the diff before creating resources:

```bash
npm run diff:free
```

Then deploy:

```bash
npm run deploy:free
```

Never commit AWS access keys, session tokens, Cognito secrets, or any other credential.

## Smoke test after deployment

Verify these in order:

1. Frontend opens successfully.
2. Demo manager login works.
3. `GET /health` returns healthy status.
4. Fleet Command loads summary and intelligence data.
5. Manager assistant answers a fleet KPI question.
6. Technician assistant answers a maintenance question using approved context.
7. Viewer assistant remains read-only.
8. Predictive ML model card loads.
9. A held-out APS sample can be scored.
10. A maintenance triage task can be created by an operator.
11. Conversation history persists when DynamoDB tables are active.
12. Governance readiness reports the free-tier-only guard and effective providers as demo/local.
13. No Bedrock request appears in logs.

## Cost boundary

This repository can prevent FleetMind from calling the metered Bedrock AI path while safe mode is enabled. It cannot guarantee that an AWS account will never incur charges from unrelated resources, account configuration, data transfer, usage above allowances, or future pricing changes.

Before and after deployment, the owner should inspect AWS Billing / Free Tier usage and remove resources that are no longer needed.

## Teardown

When the demo is no longer needed, review retained data first, then destroy the demo stacks from the same AWS account and region:

```bash
npx cdk destroy --all -c freeTierOnly=true -c production=false
```

Production-mode stacks may intentionally retain data. Do not destroy production resources without reviewing the removal policies first.
