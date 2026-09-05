import * as path from "node:path";

import { CfnOutput, Duration, RemovalPolicy, Stack, StackProps } from "aws-cdk-lib";
import * as apigatewayv2 from "aws-cdk-lib/aws-apigatewayv2";
import { HttpUserPoolAuthorizer } from "aws-cdk-lib/aws-apigatewayv2-authorizers";
import { HttpLambdaIntegration } from "aws-cdk-lib/aws-apigatewayv2-integrations";
import * as iam from "aws-cdk-lib/aws-iam";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as logs from "aws-cdk-lib/aws-logs";
import { Construct } from "constructs";
import { AuthStack } from "./auth-stack";
import { DataStack } from "./data-stack";

interface ApiStackProps extends StackProps {
  authStack: AuthStack;
  dataStack: DataStack;
  production: boolean;
  freeTierOnly: boolean;
}

export class ApiStack extends Stack {
  public readonly api: apigatewayv2.HttpApi;

  constructor(scope: Construct, id: string, props: ApiStackProps) {
    super(scope, id, props);

    const apiLogGroup = new logs.LogGroup(this, "ApiLogGroup", {
      logGroupName: "/aws/lambda/fleetmind-api",
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: props.production ? RemovalPolicy.RETAIN : RemovalPolicy.DESTROY,
    });

    const apiFunction = new lambda.DockerImageFunction(this, "FastApiFunction", {
      functionName: "fleetmind-api",
      code: lambda.DockerImageCode.fromImageAsset(
        path.join(__dirname, "../../backend"),
        { file: "Dockerfile.lambda" },
      ),
      architecture: lambda.Architecture.X86_64,
      memorySize: props.freeTierOnly ? 512 : 1536,
      timeout: Duration.seconds(30),
      logGroup: apiLogGroup,
      environment: {
        ENVIRONMENT: props.production ? "production" : "demo",
        AWS_FREE_TIER_ONLY: props.freeTierOnly ? "true" : "false",
        DEMO_MODE: props.freeTierOnly ? "true" : props.production ? "false" : "true",
        LLM_PROVIDER: props.freeTierOnly ? "demo" : props.production ? "bedrock" : "demo",
        RAG_PROVIDER: "local",
        BEDROCK_KNOWLEDGE_BASE_ID: "",
        BEDROCK_GUARDRAIL_ID: "",
        BEDROCK_GUARDRAIL_VERSION: "DRAFT",
        RAG_TOP_K: "5",
        CONVERSATIONS_TABLE: props.dataStack.conversationsTable.tableName,
        BOTS_TABLE: props.dataStack.botsTable.tableName,
        TASKS_TABLE: props.dataStack.tasksTable.tableName,
        ALLOWED_ORIGINS: "http://localhost:5173",
      },
    });

    props.dataStack.conversationsTable.grantReadWriteData(apiFunction);
    props.dataStack.botsTable.grantReadWriteData(apiFunction);
    props.dataStack.tasksTable.grantReadWriteData(apiFunction);

    if (!props.freeTierOnly) {
      apiFunction.addToRolePolicy(
        new iam.PolicyStatement({
          actions: [
            "bedrock:InvokeModel",
            "bedrock:InvokeModelWithResponseStream",
            "bedrock:Retrieve",
            "bedrock:ApplyGuardrail",
          ],
          resources: ["*"],
        }),
      );
    }

    const integration = new HttpLambdaIntegration("FastApiIntegration", apiFunction);
    const authorizer = new HttpUserPoolAuthorizer(
      "FleetMindAuthorizer",
      props.authStack.userPool,
      { userPoolClients: [props.authStack.userPoolClient] },
    );

    this.api = new apigatewayv2.HttpApi(this, "HttpApi", {
      apiName: "fleetmind-api",
      corsPreflight: {
        allowHeaders: ["authorization", "content-type"],
        allowMethods: [apigatewayv2.CorsHttpMethod.ANY],
        allowOrigins: ["http://localhost:5173"],
      },
    });

    this.api.addRoutes({
      path: "/health",
      methods: [apigatewayv2.HttpMethod.GET],
      integration,
    });
    for (const routePath of ["/", "/{proxy+}"]) {
      this.api.addRoutes({
        path: routePath,
        methods: [apigatewayv2.HttpMethod.ANY],
        integration,
        authorizer: props.production && !props.freeTierOnly ? authorizer : undefined,
      });
    }

    new CfnOutput(this, "ApiUrl", { value: this.api.apiEndpoint });
    new CfnOutput(this, "CostMode", {
      value: props.freeTierOnly ? "free-tier-only" : "standard",
    });
  }
}
