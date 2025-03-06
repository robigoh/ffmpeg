import boto3
from django.conf import settings

def upload_to_s3(file, file_name):
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY,
                       aws_secret_access_key=settings.AWS_SECRET_KEY)
    s3.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, file_name)
    return f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_name}'