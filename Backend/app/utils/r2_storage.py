import boto3
from botocore.config import Config
from flask import current_app
import uuid
import os

class R2Storage:
    def __init__(self):
        self.client = None

    def init_app(self, app):
        """Initialize R2 client with app config"""
        self.client = boto3.client(
            's3',
            endpoint_url=app.config['R2_ENDPOINT_URL'],
            aws_access_key_id=app.config['R2_ACCESS_KEY_ID'],
            aws_secret_access_key=app.config['R2_SECRET_ACCESS_KEY'],
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
        self.bucket_name = app.config['R2_BUCKET_NAME']

    def upload_file(self, file_obj, filename=None, folder='products'):
        """
        Upload a file to R2 storage

        Args:
            file_obj: File object to upload
            filename: Optional custom filename
            folder: Folder path in bucket

        Returns:
            Public URL of uploaded file
        """
        print("[R2] upload_file() called")
        print(f"[R2] File object: {file_obj}")
        print(f"[R2] Original filename: {file_obj.filename}")
        print(f"[R2] Content type: {file_obj.content_type}")

        if not filename:
            ext = os.path.splitext(file_obj.filename)[1]
            filename = f"{uuid.uuid4()}{ext}"
            print(f"[R2] Generated filename: {filename}")

        key = f"{folder}/{filename}"
        print(f"[R2] S3 Key: {key}")
        print(f"[R2] Bucket name: {self.bucket_name}")
        print(f"[R2] R2 Account ID: {current_app.config['R2_ACCOUNT_ID']}")

        try:
            print("[R2] Calling client.upload_fileobj()...")
            self.client.upload_fileobj(
                file_obj,
                self.bucket_name,
                key,
                ExtraArgs={'ContentType': file_obj.content_type}
            )
            print("[R2] upload_fileobj() completed successfully")

            # Return public URL (using public domain, not internal account ID domain)
            url = f"https://pub-bd2cbba8ae3a47b5a9244b01f8cf2e3b.r2.dev/{key}"
            print(f"[R2] Generated URL: {url}")
            return url
        except Exception as e:
            print(f"[R2] ERROR uploading to R2: {type(e).__name__}")
            print(f"[R2] Error message: {str(e)}")
            import traceback
            print(f"[R2] Traceback:\n{traceback.format_exc()}")
            return None

    def delete_file(self, file_url):
        """Delete a file from R2 storage"""
        try:
            # Extract key from URL
            key = file_url.split('.r2.dev/')[-1]
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception as e:
            print(f"Error deleting from R2: {e}")
            return False

    def get_file_url(self, key):
        """Generate a public URL for a file"""
        return f"https://pub-bd2cbba8ae3a47b5a9244b01f8cf2e3b.r2.dev/{key}"


r2_storage = R2Storage()
