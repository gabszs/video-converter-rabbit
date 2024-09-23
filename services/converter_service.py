import tempfile
from io import BytesIO

import moviepy.editor
import pika
from pika.adapters.blocking_connection import BlockingChannel

from core.dependencies import generate_short_unique_id
from core.object_storage import MinioManager
from core.settings import settings
from schemas.file_schema import QueueMessage


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
#     mp3_filename=""
# )
class Converter:
    def __init__(
        self, minio: MinioManager, rabbit_channel: BlockingChannel, save_bucket: str, download_bucket: str
    ) -> None:
        self.rabbit_channel = rabbit_channel
        self.minio = minio
        self.save_bucket = save_bucket
        self.download_bucket = download_bucket

    def __call__(self, message, channel: BlockingChannel) -> None:
        message = QueueMessage.model_validate_json(message)
        message.mp3_filename = f"{message.file_name}_{generate_short_unique_id()}"

        with tempfile.NamedTemporaryFile(
            "w+b",
        ) as file:
            video_mp3 = self.minio.download_file_to_memory(
                bucket_name=self.download_bucket, object_name=message.file_name
            )
            file.write(video_mp3)  # type: ignore
            audio = moviepy.editor.VideoFileClip(file.name).audio
            audio_buffer = BytesIO()
            audio.write_audiofile(audio_buffer, codec="mp3")
            audio_buffer.seek(0)

            self.minio.put_file(
                bucket_name=self.save_bucket,
                object_name=message.mp3_filename,
                data=audio_buffer,
                length=audio_buffer.getbuffer().nbytes,
                content_type="audio/mpeg",
            )
            audio_buffer.close()

            try:
                channel.basic_publish(
                    exchange="",
                    routing_key=settings.audio_queue,
                    body=message.model_dump(),
                    properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
                )
            except Exception:
                self.minio.delete_object(bucket_name=self.save_bucket, object_name=message.mp3_filename)
                raise
