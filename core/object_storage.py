from io import BytesIO
from typing import List
from typing import Optional
from typing import Union

from minio import Minio
from minio.error import S3Error

from core.exceptions import ObjectDownloadError
from core.exceptions import ObjectNotFoundError
from core.exceptions import ObjectStorageError
from core.exceptions import ObjectUploadError
from core.settings import settings


class MinioManager:
    def __init__(
        self,
        endpoint: str = settings.minio_endpoint,
        access_key: str = settings.minio_access_key,
        secret_key: str = settings.minio_secret_key,
        secure=False,
    ) -> None:
        self.client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

    def put_file(
        self, bucket_name: str, object_name: str, data: Union[bytearray, BytesIO], length: int, content_type: str
    ) -> None:
        self.client.put_object(bucket_name, object_name, data, length, content_type)

    def upload_file(self, bucket_name: str, object_name: str, file_path: str) -> None:
        try:
            self.client.fput_object(bucket_name, object_name, file_path)
        except FileNotFoundError:
            raise ObjectNotFoundError(f"File {file_path} not found.")
        except S3Error as e:
            raise ObjectUploadError(f"Failed to upload object {object_name} to bucket {bucket_name}: {e}")

    def download_file(self, bucket_name: str, object_name: str, file_path: str) -> None:
        try:
            self.client.fget_object(bucket_name, object_name, file_path)
        except S3Error as e:
            raise ObjectDownloadError(f"Failed to download object {object_name} from bucket {bucket_name}: {e}")

    def download_file_to_memory(self, bucket_name: str, object_name: str) -> Optional[BytesIO]:
        try:
            data = self.client.get_object(bucket_name, object_name)
            return BytesIO(data.read())
        except S3Error as e:
            raise ObjectDownloadError(
                f"Failed to download object {object_name} to memory from bucket {bucket_name}: {e}"
            )

    def list_objects(self, bucket_name: str) -> List[str]:
        try:
            return [obj.object_name for obj in self.client.list_objects(bucket_name)]
        except S3Error as e:
            raise ObjectStorageError(f"Failed to list objects in bucket {bucket_name}: {e}")

    def delete_object(self, bucket_name: str, object_name: str) -> None:
        try:
            self.client.remove_object(bucket_name, object_name)
        except S3Error as e:
            raise ObjectStorageError(f"Failed to delete object {object_name} from bucket {bucket_name}: {e}")

    def bucket_exists(self, bucket_name: str) -> bool:
        try:
            return self.client.bucket_exists(bucket_name)
        except S3Error as e:
            raise ObjectStorageError(f"Failed to check if bucket {bucket_name} exists: {e}")
