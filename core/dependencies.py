import datetime
import uuid

import pika
from pika.adapters.blocking_connection import BlockingChannel

from core.object_storage import MinioManager
from core.settings import settings
from services import Converter


connection = pika.BlockingConnection(pika.ConnectionParameters(settings.RABBIT_URL))


def generate_short_unique_id():
    timestamp = datetime.datetime.now().strftime("%y%m%d%H%M%S")  # Exemplo: 240921143055
    unique_part = uuid.uuid4().hex[:4]  # Exemplo: 'a1b2'

    return f"{timestamp}{unique_part}"


def get_rabbitmq_channel() -> BlockingChannel:
    channel = connection.channel()
    try:
        yield channel
    finally:
        channel.close()


def get_minio() -> MinioManager:
    return MinioManager()


def get_converter() -> Converter:
    rabbit_channel = get_rabbitmq_channel()
    minio = get_minio()

    return Converter(
        minio=minio,
        rabbit_channel=rabbit_channel,
        save_bucket=settings.save_bucket,
        download_bucket=settings.download_bucket,
    )
