"""
Azure Blob Storage integration for course materials.
Falls back to local file storage when Azure is not configured.
"""
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage


class CourseStorage:
    """
    Wrapper for handling course material storage.
    Uses Azure Blob Storage in production, local files in development.
    """

    def __init__(self):
        self.use_azure = settings.USE_AZURE_STORAGE

        if self.use_azure:
            try:
                from azure.storage.blob import BlobServiceClient
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    settings.AZURE_STORAGE_CONNECTION_STRING
                )
                self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
            except Exception as e:
                print(f"Azure Storage initialization failed: {e}")
                self.use_azure = False
                self.local_storage = FileSystemStorage()
        else:
            self.local_storage = FileSystemStorage()

    def upload_file(self, file_obj, blob_name):
        """Upload a file to storage"""
        if self.use_azure:
            try:
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=blob_name
                )
                blob_client.upload_blob(file_obj, overwrite=True)
                return blob_name
            except Exception as e:
                print(f"Azure upload failed: {e}")
                return self._upload_local(file_obj, blob_name)
        else:
            return self._upload_local(file_obj, blob_name)

    def _upload_local(self, file_obj, filename):
        """Upload file to local storage"""
        return self.local_storage.save(filename, file_obj)

    def get_file_url(self, blob_name):
        """Get URL for accessing a file"""
        if not blob_name:
            return None

        if self.use_azure:
            try:
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=blob_name
                )
                # Generate a SAS URL valid for 1 hour
                from azure.storage.blob import generate_blob_sas, BlobSasPermissions
                from datetime import datetime, timedelta

                # Extract account key from connection string
                conn_str = settings.AZURE_STORAGE_CONNECTION_STRING
                account_key = None
                for part in conn_str.split(';'):
                    if part.startswith('AccountKey='):
                        account_key = part.split('=', 1)[1]
                        break

                if not account_key:
                    raise ValueError("Account key not found in connection string")

                sas_token = generate_blob_sas(
                    account_name=blob_client.account_name,
                    container_name=self.container_name,
                    blob_name=blob_name,
                    account_key=account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.utcnow() + timedelta(hours=1)
                )
                return f"{blob_client.url}?{sas_token}"
            except Exception as e:
                print(f"Azure URL generation failed: {e}")
                return self._get_local_url(blob_name)
        else:
            return self._get_local_url(blob_name)

    def _get_local_url(self, filename):
        """Get URL for local file"""
        return self.local_storage.url(filename)

    def delete_file(self, blob_name):
        """Delete a file from storage"""
        if self.use_azure:
            try:
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=blob_name
                )
                blob_client.delete_blob()
                return True
            except Exception as e:
                print(f"Azure delete failed: {e}")
                return False
        else:
            try:
                self.local_storage.delete(blob_name)
                return True
            except Exception as e:
                print(f"Local delete failed: {e}")
                return False


# Global storage instance
course_storage = CourseStorage()
