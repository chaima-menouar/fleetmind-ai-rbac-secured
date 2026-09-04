# Security policy

FleetMind AI is currently a portfolio MVP and must not receive real vehicle,
customer, employee, or credential data.

## Safe configuration

- Keep `DEMO_MODE=true` for local demonstrations.
- Demo sessions are HMAC-signed by the backend and expire after the configured TTL.
- Set a private `DEMO_AUTH_SECRET` and override every demo password before any shared deployment.
- Treat the bundled test credentials and verification code as public demo values, never production secrets.
- Manager, technician, and viewer permissions are enforced again on every protected API request.
- Store AWS credentials outside the repository and use short-lived identities.
- Enable the CDK production context only after the frontend has a Cognito login flow.
- Restrict allowed origins and review Bedrock model access before deployment.
- Treat AI output as advisory; safety-critical maintenance requires a qualified technician.

## Role boundary

| Role | Allowed operations |
| --- | --- |
| Manager | Full fleet, assistant administration, knowledge uploads, and governance analytics |
| Technician | Fleet triage, predictive inference, chat, and approved technical assistants |
| Viewer | Read-only fleet summary and public model evidence; no operational actions |

Frontend route guards and role-filtered menus improve the user experience, but
the FastAPI authorization dependencies and resource checks are the authoritative
security boundary.

## Reporting

Do not open a public issue containing a secret or vulnerability exploit. Contact
the repository owner privately with reproduction steps and the affected version.
