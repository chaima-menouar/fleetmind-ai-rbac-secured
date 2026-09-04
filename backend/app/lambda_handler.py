"""AWS Lambda adapter used by the CDK Docker image."""

from mangum import Mangum

from app.main import app

handler = Mangum(app, lifespan="off")
