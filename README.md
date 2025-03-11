# PII Detection and Anonymization Solution

This solution provides an automated workflow to detect and anonymize Personally Identifiable Information (PII) in data stored in RDS MySQL databases using AWS Glue, Lambda, and Amazon Bedrock.

## Architecture

The solution consists of the following components:

1. **Data Export**: AWS Glue job connects to an RDS MySQL database and exports table data to S3
2. **PII Detection and Anonymization**: AWS Glue job processes the exported data and uses Amazon Bedrock (via Lambda) to anonymize PII
3. **Workflow Orchestration**: AWS Glue Workflow coordinates the execution of the jobs

## Directory Structure

```
PII-remove/
├── docs/                  # Documentation
│   └── README.md          # This file
├── scripts/               # Scripts for AWS Glue and Lambda
│   ├── rds_export_script.py           # Glue script to export data from RDS
│   ├── glue_pii_detect_api_v3.py      # Glue script to detect and anonymize PII
│   └── lambda_function.py             # Lambda function for Bedrock integration
└── templates/             # CloudFormation templates
    └── pii-detection-template.json    # Main CloudFormation template
```

## Deployment

### Prerequisites

- AWS CLI configured with appropriate permissions
- An RDS MySQL database with data to process
- VPC with subnets where the RDS instance is located

### Deployment Steps

1. Create S3 buckets for raw and anonymized data:

```bash
aws s3 mb s3://your-raw-data-bucket
aws s3 mb s3://your-anonymized-data-bucket
```

2. Upload the Glue scripts to the raw data bucket:

```bash
aws s3 cp scripts/rds_export_script.py s3://your-raw-data-bucket/scripts/
aws s3 cp scripts/glue_pii_detect_api_v3.py s3://your-raw-data-bucket/scripts/
```

3. Deploy the CloudFormation template:

```bash
aws cloudformation create-stack \
  --stack-name pii-detection \
  --template-body file://templates/pii-detection-template.json \
  --parameters \
    ParameterKey=RawDataBucketName,ParameterValue=your-raw-data-bucket \
    ParameterKey=AnonymizedDataBucketName,ParameterValue=your-anonymized-data-bucket \
    ParameterKey=RDSEndpoint,ParameterValue=your-rds-endpoint \
    ParameterKey=RDSPort,ParameterValue=3306 \
    ParameterKey=RDSDatabase,ParameterValue=your-database \
    ParameterKey=RDSUsername,ParameterValue=your-username \
    ParameterKey=RDSPassword,ParameterValue=your-password \
    ParameterKey=RDSTable,ParameterValue=your-table \
    ParameterKey=RDSVPCID,ParameterValue=vpc-xxxxxxxx \
    ParameterKey=RDSSubnetIDs,ParameterValue=subnet-xxxxxxxx \
  --capabilities CAPABILITY_NAMED_IAM
```

## Usage

1. Start the workflow from the AWS Glue console or using AWS CLI:

```bash
aws glue start-workflow-run --name pii-detection-workflow
```

2. Monitor the workflow execution in the AWS Glue console

3. Access the anonymized data in the anonymized data bucket

## Security Considerations

- The solution uses AWS Secrets Manager to store and retrieve database credentials
- All S3 buckets have versioning enabled and are encrypted with SSE-S3
- IAM roles follow the principle of least privilege
- VPC endpoints are used to securely access AWS services from within the VPC

## Customization

- Modify the Glue scripts to handle different data formats or anonymization requirements
- Adjust the Lambda function to use different Bedrock models or prompts
- Update the CloudFormation template to add additional resources or modify existing ones