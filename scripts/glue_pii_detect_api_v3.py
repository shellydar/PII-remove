import sys
import boto3
import json
import pandas as pd
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Get job parameters
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'source_bucket',
    'source_key',
    'target_bucket',
    'target_prefix'
])

# Initialize AWS clients
s3 = boto3.client('s3')
lambda_client = boto3.client('lambda')

def invoke_bedrock_lambda(text):
    """Invoke Bedrock Lambda function for anonymization"""
    try:
        response = lambda_client.invoke(
            FunctionName='bedrock-anonymization-lambda',
            InvocationType='RequestResponse',
            Payload=json.dumps({
                'prompt': f"Please anonymize the following text by replacing sensitive information with generic placeholders: {text}"
            })
        )
        
        payload = json.loads(response['Payload'].read().decode('utf-8'))
        if payload.get('statusCode') == 200:
            return payload.get('body', text)
        else:
            print(f"Error from Lambda: {payload}")
            return text
    except Exception as e:
        print(f"Error invoking Lambda: {str(e)}")
        return text

# Read CSV file from S3
print(f"Reading data from s3://{args['source_bucket']}/{args['source_key']}")
df = pd.read_csv(f"s3://{args['source_bucket']}/{args['source_key']}")

# Process each column
for column in df.columns:
    print(f"Processing column: {column}")
    # Convert column values to string and process
    df[column] = df[column].astype(str).apply(invoke_bedrock_lambda)

# Save anonymized data
output_key = f"{args['target_prefix']}/anonymized_{args['source_key'].split('/')[-1]}"
print(f"Saving anonymized data to s3://{args['target_bucket']}/{output_key}")

# Save to S3
df.to_csv(f"s3://{args['target_bucket']}/{output_key}", index=False)

print("Job completed successfully")
job.commit()