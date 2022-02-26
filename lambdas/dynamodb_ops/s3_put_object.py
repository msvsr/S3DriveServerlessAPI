import os
from uuid import uuid4
import logging
import boto3
from dynamodbconverters import convert_to_dynamodb_format

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # Getting region environment variables
    table, region = os.getenv('TABLE_NAME', ''), os.getenv('REGION', '')

    # Getting all the required fields from event
    event = event.get("Records")[0]
    object_creation_date = event.get("eventTime").split('T')[0]
    s3bucket = event.get("s3").get("bucket").get("name")
    s3object_key = event.get("s3").get("object").get("key")
    s3object_etag = event.get("s3").get("object").get("eTag")
    s3object_version_id = event.get("s3").get("object").get("versionId")
    dynamodb_key = str(uuid4())

    # Getting dynamodb client
    dynamodb_client = boto3.client('dynamodb', region)

    # Constructing PUT Items for dynamo db
    put_items = {
        "TableName": table,
        "Item": convert_to_dynamodb_format({
            'uuid': dynamodb_key,
            's3bucket': s3bucket,
            'object_creation_date': object_creation_date,
            's3object_key': s3object_key,
            's3object_etag': s3object_etag,
            's3object_version_id': s3object_version_id
        })
    }

    try:
        response = dynamodb_client.put_item(**put_items)
        logging.info(f"Successfully added item {dynamodb_key}")
        logging.info(f"{response}")
    except Exception as e:
        logging.info("Error: " + str(e))

