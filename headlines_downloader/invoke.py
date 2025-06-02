import boto3
import json
from datetime import datetime

lambda_client = boto3.client('lambda')

today = datetime.utcnow().strftime("%Y-%m-%d")

response = lambda_client.invoke(
    FunctionName="parcial3-dev-processor.process_headlines",
    InvocationType="RequestResponse",
    Payload=json.dumps({
        "manual": True,
        "keys": [
            f"headlines/raw/eltiempo-{today}.html",
            f"headlines/raw/publimetro-{today}.html"
        ]
    })
)

print(response['Payload'].read().decode('utf-8'))
