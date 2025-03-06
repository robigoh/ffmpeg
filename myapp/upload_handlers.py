import boto3
from django.conf import settings

s3 = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

def upload_to_s3(file_path, s3_path):
    """Upload a file to S3 bucket and return the download URL."""
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    with open(file_path, "rb") as file:
        s3.upload_fileobj(file, bucket_name, s3_path)
    return f"https://{bucket_name}.s3.amazonaws.com/{s3_path}"
