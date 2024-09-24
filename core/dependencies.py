import pika

from core.object_storage import MinioManager
from core.settings import settings

rabbit_credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
rabbit_connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=settings.RABBIT_URL, credentials=rabbit_credentials)
)


def get_minio() -> MinioManager:
    return MinioManager()
