import os
from datetime import date, timedelta
import logging
import boto3
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
from collections import Counter

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # Getting region environment variables
    table, region, sns_topic_arn = os.getenv('TABLE_NAME', ''), os.getenv('REGION', ''), os.getenv('TOPICARN', '')

    # Getting dynamodb client
    dynamodb_client = boto3.client('dynamodb', region)

    # Getting yesterday's date
    yesterday_date = str(date.today() - timedelta(days=1))

    # Constructing query for dynamo db
    # Scan: Getting all the records with yesterday's date
    scan = {
        'TableName': table,
        'Select': 'ALL_ATTRIBUTES',
        'FilterExpression': 'object_creation_date = :date',
        'ExpressionAttributeValues': TypeSerializer().serialize({':date': yesterday_date})['M']
    }

    try:
        # Getting response
        response = dynamodb_client.scan(**scan)
        logging.info(f"Successfully retrieved data using scan")

        # Converting dynamodb response to python format
        items = [{k: TypeDeserializer().deserialize(v) for k, v in x} for x in response.get('Items', [])]

        # Getting groups of data based on is_exists
        exists_content_types, deleted_content_types = [], []
        for item in items:
            if item.get('is_exists'):
                exists_content_types.append(item.get('file_content_type'))
            else:
                deleted_content_types.append(item.get('file_content_type'))

        # Counting for each file content type
        exists_content_types_counter = Counter(exists_content_types)
        deleted_content_types_counter = Counter(deleted_content_types)
        logging.info(f"No. of Objects Created: {len(exists_content_types)}, No. of Objects Deleted: {len(deleted_content_types)}")

        # Constructing message that need to published to SNS
        exists_msg = "\n".join([f"{x} : {exists_content_types_counter[x]}" for x in exists_content_types_counter])
        deletes_msg = "\n".join([f"{x} : {deleted_content_types_counter[x]}" for x in deleted_content_types_counter])
        msg = f"Create and delete operation in s3 bucket on {yesterday_date} \n " \
              f"Objects Created Content Types Count: \n {exists_msg} \n " \
              f"Objects Deleted Content Types Count: \n {deletes_msg}"

    except Exception as e:
        logging.info("Error: " + str(e))
