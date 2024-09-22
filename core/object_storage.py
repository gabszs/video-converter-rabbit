from io import BytesIO
from typing import List
from typing import Optional
from typing import Union

from aiohttp.client_reqrep import ClientResponse
from minio.error import S3Error
from miniopy_async import Minio as AsyncMinio

from core.exceptions import ObjectDownloadError
from core.exceptions import ObjectNotFoundError
from core.exceptions import ObjectStorageError
from core.exceptions import ObjectStorageimError
from core.exceptions import ObjectUploadError
from core.http_client import get_async_client
from core.settings import settings


class AsyncMinioManager:
    def __init__(
        self,
        endpoint: str = settings.minio_endpoint,
        access_key: str = settings.minio_access_key,
        secret_key: str = settings.minio_secret_key,
        secure: bool = False,
    ) -> None:
        self.client = AsyncMinio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

    async def put_file(
        self, bucket_name: str, object_name: str, data: Union[bytearray, BytesIO], length: int, content_type: str
    ) -> None:
        await self.client.put_object(bucket_name, object_name, data, length, content_type)

    async def upload_file(self, bucket_name: str, object_name: str, file_path: str) -> None:
        try:
            await self.client.fput_object(bucket_name, object_name, file_path)
        except FileNotFoundError:
            raise ObjectNotFoundError(f"File {file_path} not found.")
        except S3Error as e:
            raise ObjectUploadError(f"Failed to upload object {object_name} to bucket {bucket_name}: {e}")

    async def download_file(self, bucket_name: str, object_name: str, file_path: str) -> None:
        try:
            await self.client.fget_object(bucket_name, object_name, file_path)
        except S3Error as e:
            raise ObjectDownloadError(f"Failed to download object {object_name} from bucket {bucket_name}: {e}")

    async def download_file_to_obj(self, bucket_name: str, object_name: str) -> Optional[BytesIO]:
        try:
            data = await self.client.get_object(bucket_name, object_name)
            return BytesIO(data.read())
        except S3Error as e:
            raise ObjectDownloadError(
                f"Failed to download object {object_name} to memory from bucket {bucket_name}: {e}"
            )

    async def list_objects(self, bucket_name: str) -> List[str]:
        try:
            objects = await self.client.list_buckets
            return [obj.object_name for obj in objects]
        except S3Error as e:
            raise ObjectStorageError(f"Failed to list objects in bucket {bucket_name}: {e}")

    async def delete_object(self, bucket_name: str, object_name: str) -> None:
        try:
            await self.client.remove_object(bucket_name, object_name)
        except S3Error as e:
            raise ObjectStorageimError(f"Failed to delete object {object_name} from bucket {bucket_name}: {e}")

    async def bucket_exists(self, bucket_name: str) -> bool:
        try:
            return await self.client.bucket_exists(bucket_name)
        except S3Error as e:
            raise ObjectStorageError(f"Failed to check if bucket {bucket_name} exists: {e}")

    async def download_object(self, bucket_name: str, object_name: str) -> ClientResponse:
        async for client_session in get_async_client():
            return await self.client.get_object(bucket_name, object_name, client_session)
