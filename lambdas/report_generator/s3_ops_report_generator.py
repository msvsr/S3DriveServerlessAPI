import os
from datetime import date, timedelta
import logging
import boto3
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
import pandas as pd

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # Getting region environment variables
    table, region = os.getenv('TABLE_NAME', ''), os.getenv('REGION', '')

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

        # Grouping data using pandas
        pd_items = pd.DataFrame(items)
        items_grouped = pd_items.groupby(['is_deleted'])

        print(pd_items)

        print(items_grouped.groups)

    except Exception as e:
        logging.info("Error: " + str(e))
