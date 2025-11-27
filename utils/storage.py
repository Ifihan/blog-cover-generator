import os
from google.cloud import storage
from datetime import timedelta


class GCSStorage:
    """Handle image uploads to Google Cloud Storage."""

    def __init__(self):
        self.bucket_name = os.getenv("GCS_BUCKET_NAME")
        self.project_id = os.getenv("GCP_PROJECT_ID")

        if not self.bucket_name:
            raise ValueError("GCS_BUCKET_NAME environment variable is required")

        self.client = storage.Client(project=self.project_id)
        self.bucket = self.client.bucket(self.bucket_name)

    def upload_image(self, image_bytes, filename, username=None):
        """Upload image bytes to GCS and return storage path."""
        folder = username if username else "guest"
        blob_path = f"{folder}/{filename}"

        blob = self.bucket.blob(blob_path)
        blob.upload_from_string(image_bytes, content_type="image/png")
        blob.cache_control = "public, max-age=3600"
        blob.patch()

        return blob_path

    def delete_image(self, storage_path):
        """Delete an image from GCS using its storage path."""
        blob = self.bucket.blob(storage_path)
        blob.delete()

    def download_image(self, storage_path):
        """Download image bytes from GCS using storage path."""
        blob = self.bucket.blob(storage_path)

        if not blob.exists():
            return None

        return blob.download_as_bytes()

    def delete_user_folder(self, username):
        """Delete all images for a specific user."""
        prefix = f"{username}/"
        blobs = self.bucket.list_blobs(prefix=prefix)

        for blob in blobs:
            blob.delete()
