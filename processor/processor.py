import json
import os
import boto3
from datetime import datetime

TABLE_NAME = os.getenv("TABLE_NAME")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

def handler(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        name = body["name"]
        age = body["age"]
        cpf = body["cpf"]

        # Grava no DynamoDB
        res = table.put_item(
            Item={
                "cpf": cpf,
                "name": name,
                "age": age,
                "created_at": datetime.utcnow().isoformat()
            }
        )
        
        print(f"Pós gravação no dynamno: {res}")

        print(f"[OK] Matrícula salva no DynamoDB: {cpf} - {name}")

    return {"statusCode": 200}
