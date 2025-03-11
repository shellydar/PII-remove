import sys
import boto3
import json
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Get job parameters
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'rds_endpoint',
    'rds_port',
    'rds_database',
    'rds_table',
    'rds_secret_name',
    'target_bucket',
    'target_key'
])

# Get RDS credentials from Secrets Manager
secrets_client = boto3.client('secretsmanager')
secret_response = secrets_client.get_secret_value(SecretId=args['rds_secret_name'])
secret = json.loads(secret_response['SecretString'])
username = secret['username']
password = secret['password']

# Set up the JDBC connection properties
connection_url = f"jdbc:mysql://{args['rds_endpoint']}:{args['rds_port']}/{args['rds_database']}"
connection_properties = {
    "user": username,
    "password": password,
    "driver": "com.mysql.jdbc.Driver"
}

print(f"Connecting to {connection_url}")
print(f"Exporting table {args['rds_table']}")

# Read data from MySQL
jdbc_df = spark.read.jdbc(
    url=connection_url,
    table=args['rds_table'],
    properties=connection_properties
)

# Convert to DynamicFrame
dynamic_frame = DynamicFrame.fromDF(jdbc_df, glueContext, "dynamic_frame")

# Print schema and count
print("Schema of the data:")
dynamic_frame.printSchema()
print(f"Number of records: {dynamic_frame.count()}")

# Write to S3 as CSV
s3_path = f"s3://{args['target_bucket']}/{args['target_key']}"
print(f"Writing data to {s3_path}")

# Write as a single file
coalesced_df = jdbc_df.coalesce(1)
coalesced_df.write.mode("overwrite").option("header", "true").csv(s3_path)

print("Export completed successfully")
job.commit()