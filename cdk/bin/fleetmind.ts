#!/usr/bin/env node
import { App, Tags } from "aws-cdk-lib";
import { ApiStack } from "../lib/api-stack";
import { FrontendStack } from "../lib/frontend-stack";
import { DataStack } from "../lib/data-stack";
import { AuthStack } from "../lib/auth-stack";

const app = new App();
const production = app.node.tryGetContext("production") === "true";
const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION ?? "us-east-1",
};

const auth = new AuthStack(app, "FleetMindAuthStack", { env });
const data = new DataStack(app, "FleetMindDataStack", { env, production });
const api = new ApiStack(app, "FleetMindApiStack", {
  env,
  authStack: auth,
  dataStack: data,
  production,
});
new FrontendStack(app, "FleetMindFrontendStack", {
  env,
  api: api.api,
  production,
});

Tags.of(app).add("Project", "FleetMindAI");
Tags.of(app).add("Environment", production ? "production" : "demo");
