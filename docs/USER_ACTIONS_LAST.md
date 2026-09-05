# FleetMind — user actions left for the very end

Everything in this file is intentionally deferred until after code-side work is complete.

## 1. AWS account-side actions

These actions require the repository owner because they affect the AWS account rather than source code:

1. Choose the AWS region to use for the demo deployment.
2. Confirm the account is on the intended AWS Free plan / Free Tier and review the current monthly allowances for the chosen region and account age.
3. Configure AWS CLI credentials locally or use an authenticated AWS shell/profile. Do not commit keys to GitHub.
4. Bootstrap CDK once for the selected account/region if it has never been bootstrapped.
5. Run the free-tier-safe deployment command from `cdk/`:

   ```bash
   npm run deploy:free
   ```

6. Record the CloudFormation outputs for API URL and frontend URL.
7. Verify the deployed app with the smoke-test checklist in `docs/AWS_FREE_TIER_DEPLOYMENT.md`.

## 2. Services intentionally not activated in free-tier-safe mode

The following integrations remain implemented in code but are intentionally disabled while `AWS_FREE_TIER_ONLY=true`:

- Amazon Bedrock model inference;
- Amazon Bedrock Knowledge Bases retrieval;
- Amazon Bedrock Guardrails.

They are metered AI services and are not needed to demonstrate the portfolio architecture.

## 3. Optional authentication action

Amazon Cognito support remains in the repository. Live viewer email verification can be configured later, but it is not required for the free-tier-safe portfolio deployment. Demo manager/technician/viewer sessions are sufficient for the portfolio walkthrough.

## 4. Final limits to measure after deployment

After the first live AWS deployment, test and record:

- cold-start latency of the Lambda API;
- response time for fleet dashboard endpoints;
- DynamoDB persistence across Lambda restarts;
- CloudWatch log volume;
- API Gateway request volume;
- frontend delivery behavior;
- maximum practical demo concurrency before latency becomes noticeable;
- the exact AWS Free Tier / Free plan usage shown in the Billing console.

Do not guess these values in the README. Measure them from the live account and keep the portfolio claims evidence-based.

## 5. Success condition

The AWS demo is considered complete when:

- the application is reachable publicly;
- role-scoped demo login works;
- fleet intelligence works;
- predictive ML inference works;
- assistant answers remain grounded in deterministic fleet data and the local approved RAG corpus;
- conversations/tasks persist through DynamoDB when configured;
- governance reports `AWS free-tier-only` mode and no Bedrock provider is active;
- no unexpected AWS charge-generating AI service is enabled.
