# API guide

The interactive OpenAPI documentation is available at
<http://localhost:8000/docs> while the backend is running.

## Health

~~~bash
curl http://localhost:8000/health
~~~

## Sign in

The local demo validates credentials on the backend and returns an expiring,
signed bearer token:

~~~bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"technician@fleetmind.demo","password":"Service2026!"}'
~~~

Copy the returned access_token for the following examples:

~~~bash
TOKEN="<access_token>"
~~~

## List assistants

~~~bash
curl "http://localhost:8000/api/bots?shared_only=true" \
  -H "Authorization: Bearer $TOKEN"
~~~

## Send a grounded message

~~~bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "technician",
    "content": "How should we triage a battery warning on FM-4410?"
  }'
~~~

Reuse the returned conversation_id in later messages to maintain a local
history.

## Create an assistant

This operation and knowledge uploads require a manager token. Sign in with the
manager test account and replace TOKEN before running these examples.

~~~bash
curl -X POST http://localhost:8000/api/bots \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Warranty Assistant",
    "department": "support",
    "description": "Helps agents explain enterprise fleet warranty coverage.",
    "system_prompt": "Answer using approved warranty material and state uncertainty.",
    "is_shared": true
  }'
~~~

## Attach local knowledge

The MVP accepts UTF-8 .txt, .md, and .csv files up to the configured upload
limit.

~~~bash
curl -X POST http://localhost:8000/api/bots/technician/knowledge \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@../examples/technician-bot/knowledge/ev-safety.md"
~~~

## Run maintenance triage

~~~bash
curl -X POST http://localhost:8000/api/agents/run \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"task_type":"maintenance_triage","vehicle_id":"FM-4410"}'
~~~

Demo vehicle IDs are returned by:

~~~bash
curl http://localhost:8000/api/fleet/summary \
  -H "Authorization: Bearer $TOKEN"
~~~

## Authentication behavior

With DEMO_MODE=true, login and viewer registration are handled by the local
server adapter. It issues signed, expiring sessions and never accepts a role
chosen by the browser. With DEMO_MODE=false, requests must arrive through the
Cognito-authorized API Gateway route; the backend reads verified JWT claims
from the Lambda event.

The API enforces these role boundaries:

| Capability | Manager | Technician | Viewer |
| --- | --- | --- | --- |
| Fleet summary | Yes | Yes | Read only |
| Predictive inference and triage | Yes | Yes | No |
| Chat and approved assistants | All | Technical only | No |
| Create assistants and upload knowledge | Yes | No | No |
| Usage and governance | Yes | No | No |

## Inspect the trained APS model

~~~bash
curl http://localhost:8000/api/ml/model-card \
  -H "Authorization: Bearer $TOKEN"
~~~

The response includes dataset provenance, split sizes, threshold-selection
costs, held-out metrics, runtime versions, and limitations.

## Run a model prediction

List the bundled examples from the untouched official test split:

~~~bash
curl http://localhost:8000/api/ml/samples \
  -H "Authorization: Bearer $TOKEN"
~~~

Then score one sample on the backend:

~~~bash
curl -X POST http://localhost:8000/api/ml/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sample_id":"test-example-01"}'
~~~

The response contains the calibrated APS score, the cost-sensitive decision
threshold, predicted and actual labels, and the exact model version. These
examples are for reproducible evaluation; the fictional Fleet overview vehicles
do not contain the model's 170 anonymized inputs.
