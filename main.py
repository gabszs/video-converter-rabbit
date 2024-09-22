import asyncio
import os
import sys

from core.dependencies import get_async_minio
from core.dependencies import get_rabbitmq_channel
from core.settings import settings
from services import Converter


async def main():
    channel = get_rabbitmq_channel()
    minio = get_async_minio()

    converter = Converter(
        minio=minio, rabbit_channel=channel, save_bucket=settings.save_bucket, download_bucket=settings.download_bucket
    )

    async def callback(channel, method, properties, body):
        try:
            converter(body, channel)
            channel.basic_nack(delivery_tag=method.delivery_tag)
        except Exception:
            channel.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=settings.video_queue, on_message_callback=callback)

    channel.start_consuming()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
