import { CfnOutput, RemovalPolicy, Stack, StackProps } from "aws-cdk-lib";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";
import { Construct } from "constructs";

interface DataStackProps extends StackProps {
  production: boolean;
}

export class DataStack extends Stack {
  public readonly conversationsTable: dynamodb.Table;
  public readonly botsTable: dynamodb.Table;
  public readonly tasksTable: dynamodb.Table;

  constructor(scope: Construct, id: string, props: DataStackProps) {
    super(scope, id, props);

    const removalPolicy = props.production ? RemovalPolicy.RETAIN : RemovalPolicy.DESTROY;

    this.conversationsTable = new dynamodb.Table(this, "Conversations", {
      tableName: "fleetmind-conversations",
      partitionKey: { name: "conversationId", type: dynamodb.AttributeType.STRING },
      sortKey: { name: "createdAt", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      pointInTimeRecoverySpecification: { pointInTimeRecoveryEnabled: props.production },
      removalPolicy,
    });

    this.botsTable = new dynamodb.Table(this, "Bots", {
      tableName: "fleetmind-bots",
      partitionKey: { name: "id", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      pointInTimeRecoverySpecification: { pointInTimeRecoveryEnabled: props.production },
      removalPolicy,
    });

    this.tasksTable = new dynamodb.Table(this, "Tasks", {
      tableName: "fleetmind-agent-tasks",
      partitionKey: { name: "taskId", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      pointInTimeRecoverySpecification: { pointInTimeRecoveryEnabled: props.production },
      removalPolicy,
    });

    new CfnOutput(this, "ConversationsTableName", { value: this.conversationsTable.tableName });
    new CfnOutput(this, "BotsTableName", { value: this.botsTable.tableName });
    new CfnOutput(this, "TasksTableName", { value: this.tasksTable.tableName });
  }
}
