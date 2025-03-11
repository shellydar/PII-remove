import json
import boto3
import os

bedrock_runtime = boto3.client('bedrock-runtime')

def lambda_handler(event, context):
    prompt = event.get('prompt')
    model_id = event.get('model', 'anthropic.claude-3-sonnet-20240229-v1:0')
    
    if not prompt:
        return {
            'statusCode': 400,
            'body': json.dumps('Prompt is required')
        }
    
    try:
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "temperature": 0.2,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response['body'].read().decode('utf-8'))
        content = response_body['content'][0]['text']
        
        return {
            'statusCode': 200,
            'body': content
        }
    except Exception as e:
        print(f"Error invoking Bedrock model: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }