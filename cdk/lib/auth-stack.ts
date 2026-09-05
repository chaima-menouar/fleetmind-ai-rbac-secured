import { CfnOutput, Duration, RemovalPolicy, Stack, StackProps } from "aws-cdk-lib";
import * as cognito from "aws-cdk-lib/aws-cognito";
import { Construct } from "constructs";

export class AuthStack extends Stack {
  public readonly userPool: cognito.UserPool;
  public readonly userPoolClient: cognito.UserPoolClient;

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    this.userPool = new cognito.UserPool(this, "UserPool", {
      userPoolName: "fleetmind-users",
      selfSignUpEnabled: true,
      signInAliases: { email: true },
      autoVerify: { email: true },
      accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,
      passwordPolicy: {
        minLength: 12,
        requireDigits: true,
        requireLowercase: true,
        requireSymbols: true,
        requireUppercase: true,
      },
      customAttributes: {
        department: new cognito.StringAttribute({ mutable: true, minLen: 2, maxLen: 40 }),
        role: new cognito.StringAttribute({ mutable: true, minLen: 5, maxLen: 20 }),
      },
      removalPolicy: RemovalPolicy.RETAIN,
    });

    const writeAttributes = new cognito.ClientAttributes()
      .withStandardAttributes({ email: true, fullname: true });

    this.userPoolClient = this.userPool.addClient("WebClient", {
      userPoolClientName: "fleetmind-web",
      authFlows: { userPassword: true, userSrp: true },
      writeAttributes,
      preventUserExistenceErrors: true,
      accessTokenValidity: Duration.minutes(60),
      idTokenValidity: Duration.minutes(60),
      refreshTokenValidity: Duration.days(30),
    });

    new cognito.CfnUserPoolGroup(this, "AdminGroup", {
      groupName: "admin",
      userPoolId: this.userPool.userPoolId,
      description: "FleetMind administrators",
    });

    new cognito.CfnUserPoolGroup(this, "TechnicianGroup", {
      groupName: "technician",
      userPoolId: this.userPool.userPoolId,
      description: "FleetMind maintenance technicians",
    });

    new cognito.CfnUserPoolGroup(this, "ViewerGroup", {
      groupName: "viewer",
      userPoolId: this.userPool.userPoolId,
      description: "FleetMind read-only viewers",
    });

    new CfnOutput(this, "UserPoolId", { value: this.userPool.userPoolId });
    new CfnOutput(this, "UserPoolClientId", { value: this.userPoolClient.userPoolClientId });
  }
}
