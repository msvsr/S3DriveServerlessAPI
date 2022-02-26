import os
import json
import logging
import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # Getting region environment variables
    region = os.getenv('REGION', '')

    print(event)
