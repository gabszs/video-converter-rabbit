from typing import Optional

from pydantic import BaseModel
from pydantic import constr
from pydantic import field_validator


class FileMetadata(BaseModel):
    file_name: constr(min_length=1)  # type: ignore
    content_type: Optional[str]

    @field_validator("content_type")
    def check_content_type(cls, extension):
        allowed_video_types = [
            "video/mp4",
            "video/x-matroska",  # .mkv
            "video/avi",
            "video/webm",
            "video/ogg",
        ]
        if extension not in allowed_video_types:
            raise ValueError("File Type not allowed, please send a video file")
        return extension


class QueueMessage(FileMetadata):
    client_email: str
    mp3_filename: Optional[str]
