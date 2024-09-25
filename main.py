import os
import sys

from icecream import ic

from core.dependencies import get_minio
from core.dependencies import rabbit_connection
from core.settings import settings
from services import Converter


def main():
    minio = get_minio()

    with rabbit_connection.channel() as channel:
        channel.queue_declare(queue=settings.video_queue, durable=True)

        converter = Converter(minio=minio, rabbit_channel=channel)

        def callback(channel, method, properties, body):  # callback does not support async context
            print("Received message:", body.decode())
            try:
                converter(body, channel)
                channel.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as error:
                ic(error)
                channel.basic_nack(delivery_tag=method.delivery_tag)

        channel.basic_consume(queue=settings.video_queue, on_message_callback=callback)
        print('Waiting for messages in the "video" queue. To exit press CTRL+C')
        channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        try:
            ic("Queue interrupted")
            sys.exit(0)
        except SystemExit:
            os._exit(0)
