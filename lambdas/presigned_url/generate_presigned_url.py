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

    # setting expires in
    expires_in = 10

    # Getting file name from path parameters
    filename = event.get('pathParameters', {}).get('filename', '')

    # Getting mime type
    content_type = mimetypes.MimeTypes().guess_type(filename)[0]

    logging.info(f"Filename: {filename}, Content Type: {content_type}")

    # Checking for content-type
    if not content_type:
        return {
            'statusCode': 200,
            'body': json.dumps({
                "message": "Please provide a valid file extension. Refer this URL for valid file extensions "
                           "https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types"
            })
        }

    # Initializing s3 client
    s3_client = boto3.client('s3', region, config=Config(signature_version='s3v4'))

    # Generating pre_signed_url
    pre_signed_url = s3_client.generate_presigned_post(
        Bucket=s3_bucket,
        Key="uploads/"+filename,
        ExpiresIn=expires_in*60
    )

    # Returning response
    return {
        'statusCode': 200,
        'body': json.dumps({
            "URL and Fields": pre_signed_url,
            "This link will expire in minutes": expires_in
        })
    }
