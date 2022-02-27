import os
import logging
import boto3
import mimetypes
from boto3.dynamodb.types import TypeSerializer


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # Getting region environment variables
    table, region = os.getenv('TABLE_NAME', ''), os.getenv('REGION', '')

    # Getting all the required fields from event
    event = event.get("Records")[0]
    object_creation_date, object_creation_time = event.get("eventTime").split('T')
    bucket = event.get("s3").get("bucket").get("name")
    object_key = event.get("s3").get("object").get("key")
    object_etag = event.get("s3").get("object").get("eTag")
    object_version_id = event.get("s3").get("object").get("versionId")
    content_type = mimetypes.MimeTypes().guess_type(object_key)[0]  # Getting mime type

    # Getting dynamodb client
    dynamodb_client = boto3.client('dynamodb', region)

    # Constructing PUT Items for dynamo db
    put_items = {
        "TableName": table,
        "Item": TypeSerializer().serialize({
            'object_key': object_key,
            'object_version_id': object_version_id,
            'bucket': bucket,
            'object_creation_date': object_creation_date,
            'object_creation_time': object_creation_time,
            'object_etag': object_etag,
            'file_content_type': content_type,
            'is_deleted': False
        })['M']
    }

    try:
        response = dynamodb_client.put_item(**put_items)
        logging.info(f"Successfully added item to DynamoDB. Partition Key: {object_key}, Sort Key: {object_version_id}")
        logging.info(f"{response}")
    except Exception as e:
        logging.info("Error: " + str(e))

