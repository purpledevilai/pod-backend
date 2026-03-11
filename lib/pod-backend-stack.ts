import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import path from 'path';

export class PodBackendStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Secrets Manager
    const appSecret = new secretsmanager.Secret(this, 'AppSecret', {
      secretName: 'secrets',
      secretObjectValue: {},
    });

    // Users Table
    const usersTable = new dynamodb.Table(this, 'users', {
      tableName: 'users',
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });
    usersTable.addGlobalSecondaryIndex({
      indexName: 'email',
      partitionKey: { name: 'email', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // Challenge Table
    const challengesTable = new dynamodb.Table(this, 'challenges', {
      tableName: 'challenges',
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Post Code to Council Table
    const postcodeToCouncilTable = new dynamodb.Table(this, 'postcode_to_council', {
      tableName: 'postcode_to_council',
      partitionKey: { name: 'postcode', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Councils Table
    const councilsTable = new dynamodb.Table(this, 'councils', {
      tableName: 'councils',
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Council to Bin System Table
    const councilToBinSystemTable = new dynamodb.Table(this, 'council_to_bin_system', {
      tableName: 'council_to_bin_system',
      partitionKey: { name: 'council_id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Bin Systems Table
    const binSystemsTable = new dynamodb.Table(this, 'bin_systems', {
      tableName: 'bin_systems',
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });


    // Requirements Layer
    const requirementsLayer = new lambda.LayerVersion(this, 'requirementsLayer', {
      code: lambda.Code.fromAsset(path.join(__dirname, '..', 'layers', 'requirements', 'requirements-layer.zip')),
      compatibleRuntimes: [
        lambda.Runtime.PYTHON_3_11,
      ],
    });

    // API Lambda Function
    const apiLambda = new lambda.Function(this, 'APILambda', {
      functionName: 'api',
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'app.lambda_handler',
      code: lambda.Code.fromAsset('lambda/api'),
      timeout: cdk.Duration.seconds(30),
      layers: [requirementsLayer],
      environment: {
        'SECRET_ARN': appSecret.secretArn,
      }
    });
    usersTable.grantReadWriteData(apiLambda)
    challengesTable.grantReadWriteData(apiLambda)
    postcodeToCouncilTable.grantReadData(apiLambda)
    councilsTable.grantReadData(apiLambda)
    councilToBinSystemTable.grantReadData(apiLambda)
    binSystemsTable.grantReadData(apiLambda)

    // Grant Lambda permissions to read the secret
    appSecret.grantRead(apiLambda);

    apiLambda.addToRolePolicy(new iam.PolicyStatement({
      actions: ['ses:SendEmail', 'ses:SendRawEmail'],
      resources: ['*'],
    }));

    // API Gateway
    new apigateway.LambdaRestApi(this, 'APIGateway', {
      handler: apiLambda,
      proxy: true,
    });

    // RecycleMate Data Refresh Lambda (TypeScript, bundled with esbuild)
    const refreshDataLambda = new NodejsFunction(this, 'RefreshDataLambda', {
      functionName: 'refresh-recyclemate-data',
      entry: path.join(__dirname, '..', 'lambda', 'refresh-data', 'index.ts'),
      handler: 'handler',
      runtime: lambda.Runtime.NODEJS_20_X,
      timeout: cdk.Duration.minutes(15),
      memorySize: 512,
      bundling: {
        minify: true,
        sourceMap: true,
      },
    });

    postcodeToCouncilTable.grantWriteData(refreshDataLambda);
    councilsTable.grantWriteData(refreshDataLambda);
    councilToBinSystemTable.grantWriteData(refreshDataLambda);
    binSystemsTable.grantWriteData(refreshDataLambda);

    // Weekly schedule — every Monday at 02:00 UTC
    new events.Rule(this, 'RefreshDataWeeklyRule', {
      schedule: events.Schedule.cron({ minute: '0', hour: '2', weekDay: 'MON' }),
      targets: [new targets.LambdaFunction(refreshDataLambda)],
    });
  }
}
