import os

def extract_filename(url):
    """Extracts filename from S3 URL"""
    return os.path.basename(url).split(".")[0]
