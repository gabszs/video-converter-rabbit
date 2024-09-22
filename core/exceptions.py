from typing import Any


class ObjectStorageError(Exception):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(detail)
        self.detail = detail


class ObjectStorageimError(Exception):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(detail or "An error occurred with the object storage implementation.")
        self.detail = detail or "An error occurred with the object storage implementation."


class ObjectNotFoundError(Exception):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(detail or "Object not found in storage.")
        self.detail = detail or "Object not found in storage."


class ObjectAlreadyExistsError(Exception):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(detail or "Object already exists in storage.")
        self.detail = detail or "Object already exists in storage."


class ObjectUploadError(Exception):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(detail or "Failed to upload object to storage.")
        self.detail = detail or "Failed to upload object to storage."


class ObjectDownloadError(Exception):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(detail or "Failed to download object from storage.")
        self.detail = detail or "Failed to download object from storage."
