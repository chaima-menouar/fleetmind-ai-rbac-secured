# AWS free-tier-safe mode

FleetMind defaults to a cost-safe AWS deployment profile designed for portfolio and learning use.

## What the mode does

`AWS_FREE_TIER_ONLY=true` is the application cost guard. The CDK app also defaults `freeTierOnly` to true.

While this mode is enabled:

- the chat runtime uses FleetMind's deterministic credential-free AI gateway;
- retrieval stays on the local approved RAG corpus;
- Amazon Bedrock model inference is blocked even if `LLM_PROVIDER=bedrock` is set accidentally;
- Bedrock Knowledge Bases retrieval is blocked;
- Bedrock Guardrails are not called;
- the default Lambda role is not granted Bedrock invocation/retrieval/guardrail permissions;
- Lambda memory is reduced to 512 MB and log retention is one week;
- DynamoDB persistence remains available when the CDK tables are deployed;
- the React/FastAPI application, predictive Scania APS model, grounded fleet analytics, RBAC, audit logging, and local RAG continue to work.

## AWS services used by the safe cloud path

The infrastructure can use the following AWS services without enabling metered generative AI:

- AWS Lambda for the FastAPI backend;
- Amazon API Gateway for HTTP routing;
- Amazon DynamoDB for conversations, assistants, and agent tasks;
- Amazon S3 and Amazon CloudFront for the frontend path;
- Amazon CloudWatch Logs for application/audit logs;
- Amazon Cognito remains optional.

AWS currently lists these services among services available through its Free Tier / new Free account experience. Free usage still has account-plan, credit, time, and monthly-usage limits. This repository does not claim that an AWS resource is permanently zero-cost outside those limits.

## Why Bedrock is disabled in this mode

Amazon Bedrock is usage-priced. New AWS customers may have Free Tier credits that can cover experiments, but FleetMind does not rely on those credits for its default no-surprise-cost path. The Bedrock code remains available as an optional architecture extension only after `freeTierOnly` is explicitly disabled.

## CDK commands

Default safe synthesis:

```bash
cd cdk
npm run build
npx cdk synth
```

Explicit safe production-shaped synthesis:

```bash
npx cdk synth -c production=true -c freeTierOnly=true
```

A standard metered AI path requires an explicit opt-out:

```bash
npx cdk synth -c production=true -c freeTierOnly=false
```

Do not use the standard path unless the AWS account owner has reviewed pricing, budgets, and service limits.

## Runtime evidence

Managers can inspect `/api/admin/readiness`. In safe mode it reports:

- `aws_free_tier_only: true`;
- `cost_guard: metered generative AI blocked`;
- effective LLM provider `demo`;
- effective RAG provider `local`.

This makes the cost boundary visible instead of relying on documentation alone.
