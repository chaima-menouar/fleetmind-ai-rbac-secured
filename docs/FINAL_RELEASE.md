# FleetMind AI — portfolio release

FleetMind is considered complete for portfolio use at this milestone.

## What the release demonstrates

- **AI engineering:** role-scoped assistants, grounded generation, retrieval context, and anti-hallucination boundaries.
- **Machine learning:** a reproducible Scania APS classifier with held-out evaluation, model-card evidence, threshold-aware inference, and explainability boundaries.
- **Backend engineering:** FastAPI contracts, RBAC, owner-scoped resources, deterministic fleet analytics, maintenance-agent orchestration, and governance endpoints.
- **Frontend engineering:** responsive React/TypeScript dashboards for managers, technicians, and viewers.
- **Cloud engineering:** Amazon Bedrock integration and AWS CDK architecture for Cognito, DynamoDB, Lambda, API Gateway, S3, and CloudFront.
- **Security:** signed demo sessions, server-enforced least privilege, upload validation, restricted CORS, and optional Cognito verification path.
- **MLOps / quality:** artifact integrity verification and CI for backend lint/type/tests, frontend build, and infrastructure validation.

## Trust boundaries

FleetMind intentionally keeps three evidence types separate:

1. **Fictional fleet telemetry** powers the portfolio fleet dashboard and deterministic operational-risk demo.
2. **Real Scania APS data** powers the independently evaluated predictive-maintenance classifier.
3. **Generative AI** explains verified analytics and approved knowledge; it is not trusted to invent telemetry or calculate fleet KPIs.

The APS features are anonymized. The UI therefore explains score, threshold distance, evaluation truth, and action scope without inventing physical sensor meanings.

## Runtime governance

Managers can inspect `/api/admin/readiness` through the governance dashboard. The endpoint reports non-secret evidence including:

- active environment and LLM provider;
- grounding architecture;
- predictive-model artifact state and version;
- persistence mode;
- authentication capability;
- configured CORS-origin count.

## What is intentionally not claimed

This is not a production fleet-control or safety system. It does not claim:

- live OEM telemetry integration;
- production ticketing/CRM integrations;
- validated safety-critical deployment;
- enterprise tenant persistence;
- a production vector database or knowledge base;
- completed live Cognito/Vercel verification.

Those are future enterprise integrations, not blockers for the portfolio release.
