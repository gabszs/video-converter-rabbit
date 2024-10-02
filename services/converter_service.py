import datetime
import os
import tempfile
import uuid
from typing import Dict

import pika
from audio_extract import extract_audio
from pika.adapters.blocking_connection import BlockingChannel

from core.object_storage import MinioManager
from core.settings import settings
from schemas.file_schema import QueueMessage

from pathlib import Path

# pega a messagem que veio, e extrai o json
# abre um arquivo temporario
# pega esse arquivo, e escreve nele o mp4
# edita, pega o agudio, passa ele pro objeto, e armaazena no objeto
# fecha o arquivo temporario
# pega o objeto e salva novo no no arquivo temporario denovo,
# depois abre ele denovo, ele elete, e coloca ele no storage
# depois de salvar novamente decha o arquivo temporario, lllkkkkkk
# atribui o id do arquivo na menssage, e manda para a fila
# joga a menssagem no na fila do mp3_audio para notificar o cliente
# se dar ruim voce remove do storage
# QueueMessage(
#     file_name="",
#     content_type="",
#      mp3_filename=""
# )

video_types: Dict[str, str] = {
    "video/mp4": ".mp4",
    "video/x-matroska": ".mkv",  # Matroska format
    "video/avi": ".avi",
    "video/webm": ".webm",
    "video/ogg": ".ogg",
}


def generate_short_unique_id():
    timestamp = datetime.datetime.now().strftime("%y%m%d%H%M%S")
    unique_part = uuid.uuid4().hex[:4]

    return f"{timestamp}{unique_part}"

def get_save_filename(message_filename: str, file_suffix: str = "mp3") -> str:
    file = Path(message_filename)
    random_id = generate_short_unique_id()
    return str(file.with_name(f"{random_id}_{file.stem}.{file_suffix}"))

class Converter:
    def __init__(
        self,
        minio: MinioManager,
        rabbit_channel: BlockingChannel,
        audio_bucket: str = settings.audio_bucket,
        video_bucket: str = settings.video_bucket,
    ) -> None:
        self.rabbit_channel = rabbit_channel
        self.minio = minio
        self.audio_bucket = audio_bucket
        self.video_bucket = video_bucket

    def __call__(self, queue_message: bytes, channel: BlockingChannel) -> None:
        message = QueueMessage.model_validate_json(queue_message)
        file_save_name = get_save_filename(message.file_name)
        video_type: str = video_types[message.content_type]  # type: ignore

        try:
            with tempfile.NamedTemporaryFile("w+b", suffix=".mp3", delete=False) as audio_file:
                audio_file_name = audio_file.name

            with tempfile.NamedTemporaryFile(suffix=video_type) as video_file:
                self.minio.download_file(
                    bucket_name=self.video_bucket, object_name=message.file_name, file_path=video_file.name
                )

                extract_audio(input_path=video_file.name, output_path=audio_file_name, overwrite=True)

                self.minio.upload_file(
                    bucket_name=self.video_bucket, object_name=file_save_name, file_path=audio_file_name
                )
                os.remove(audio_file_name)
                channel.basic_publish(
                    exchange="",
                    routing_key=settings.audio_queue,
                    body=message.model_dump_json(),
                    properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
                )
                print(f"Audio file {audio_file_name} removed and message successfully sent to queue {settings.audio_queue}.")

        except Exception:
            if os.path.exists(audio_file_name):
                os.remove(audio_file_name)
            self.minio.delete_object(bucket_name=self.audio_bucket, object_name=file_save_name)
            raise
