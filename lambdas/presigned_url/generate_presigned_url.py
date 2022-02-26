import os
import json
import logging
import boto3
import mimetypes
from botocore.config import Config

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):

    # Getting s3 bucket and region from environment variables
    s3_bucket, region = os.getenv('BUCKET_NAME', ''), os.getenv('REGION', '')
    # Getting file name from path parameters
    filename = event.get('pathParameters', {}).get('filename', '')
    # Getting mime type
    content_type = mimetypes.MimeTypes().guess_type(filename)[0]

    logging.info(f"Filename: {filename}, Content Type: {content_type}")

    # Initializing s3 client
    s3_client = boto3.client('s3', region, config=Config(signature_version='s3v4'))

    # Generating pre_signed_url - Got
    pre_signed_url = s3_client.generate_presigned_post(
        Bucket=s3_bucket,
        Key=filename,
        ExpiresIn=600
    )

    # Returning response
    return {
        'statusCode': 200,
        'body': json.dumps(pre_signed_url)
    }
