import boto3
import os
import datetime


def save_to_s3(text: str):
    s3 = boto3.client("s3")
    filename = f"raw/{datetime.datetime.now().isoformat()}.txt"
    s3.put_object(Bucket=os.getenv("S3_BUCKET_NAME"), Key=filename, Body=text)
