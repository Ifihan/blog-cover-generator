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

    def upload_image(self, image_bytes, filename):
        """Upload image bytes to GCS and return public URL."""
        blob = self.bucket.blob(f"blog-covers/{filename}")
        blob.upload_from_string(image_bytes, content_type="image/png")
        blob.cache_control = "public, max-age=3600"
        blob.patch()

        return f"https://storage.googleapis.com/{self.bucket_name}/blog-covers/{filename}"

    def delete_image(self, filename):
        """Delete an image from GCS."""
        blob = self.bucket.blob(f"blog-covers/{filename}")
        blob.delete()

    def generate_signed_url(self, filename, expiration_minutes=60):
        """Generate a signed URL for private image access."""
        blob = self.bucket.blob(f"blog-covers/{filename}")
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET",
        )
        return url
