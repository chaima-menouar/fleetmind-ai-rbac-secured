# Contributing

1. Create a branch from `main`.
2. Keep secrets and real customer/vehicle data out of commits.
3. Run the backend tests, frontend build, and CDK synthesis locally.
4. Open a pull request with the problem, solution, and verification steps.

## Local quality checks

```bash
cd backend
poetry run ruff check app tests
poetry run mypy app
poetry run pytest

cd ../frontend
npm run build

cd ../cdk
npm run build
npm run synth
```

Do not connect a new production data source until its retention, access, and
redaction rules are documented.
