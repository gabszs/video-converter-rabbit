import pytest
from pydantic import ValidationError

from schemas.file_schema import FileMetadata
from schemas.file_schema import QueueMessage


def test_file_metadata_valid():
    metadata = FileMetadata(file_name="video.mp4", content_type="video/mp4")
    assert metadata.file_name == "video.mp4"
    assert metadata.content_type == "video/mp4"


def test_file_metadata_invalid_content_type():
    with pytest.raises(ValidationError) as excinfo:
        FileMetadata(file_name="video.mp4", content_type="image/png")
    assert "File Type not allowed, please send a video file" in str(excinfo.value)


def test_file_metadata_missing_file_name():
    with pytest.raises(ValidationError) as excinfo:
        FileMetadata(content_type="video/mp4")
    errors = excinfo.value.errors()
    assert any(error["loc"] == ("file_name",) and error["type"] == "missing" for error in errors)


def test_queue_message_valid():
    message = QueueMessage(
        file_name="video.mp4", content_type="video/mp4", client_email="client@example.com", mp3_filename=None
    )
    assert message.file_name == "video.mp4"
    assert message.content_type == "video/mp4"
    assert message.client_email == "client@example.com"
    assert message.mp3_filename is None


def test_queue_message_invalid_content_type():
    with pytest.raises(ValidationError) as excinfo:
        QueueMessage(file_name="video.mp4", content_type="image/jpeg", client_email="client@example.com")
    assert "File Type not allowed, please send a video file" in str(excinfo.value)


def test_queue_message_missing_client_email():
    with pytest.raises(ValidationError) as excinfo:
        QueueMessage(file_name="video.mp4", content_type="video/mp4", mp3_filename=None)

    assert "client_email" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)
