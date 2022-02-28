import os
import re
import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # Getting s3 bucket and region from environment variables
    sns_topic_arn, region = os.getenv('SNSTOPIC', ''), os.getenv('REGION', '')

    # Getting file name from path parameters
    email = event.get('pathParameters', {}).get('email', '')
    logging.info(f"email: {email}")

    # Validating Email
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(regex, email):
        logging.info("Valid Email")
    else:
        return {
            'statusCode': 200,
            'body': json.dumps({
                "message": "Please provide a valid email"
            })
        }

    # Initializing sns client
    sns_client = boto3.client('sns', region)
    try:
        # Subscribing to sns topic
        response = sns_client.subscribe(
            TopicArn=sns_topic_arn,
            Protocol="email",
            Endpoint=email
        )

        logging.info(f"Subscription ARN: {response.get('SubscriptionArn', '')}")

        # Returning response
        return {
            'statusCode': 200,
            'body': json.dumps({
                 "Message": f"Please validate your email {email}"
            })
        }
    except Exception as e:
        logging.info(f"Error: {str(e)}")
