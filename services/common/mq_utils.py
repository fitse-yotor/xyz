import pika
import json
import os
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(
                os.getenv('RABBITMQ_USER', 'admin'),
                os.getenv('RABBITMQ_PASSWORD', 'admin123')
            )
            parameters = pika.ConnectionParameters(
                host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),
                port=int(os.getenv('RABBITMQ_PORT', 5672)),
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("Successfully connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise

    def declare_queue(self, queue_name: str):
        """Declare a queue"""
        self.channel.queue_declare(queue=queue_name, durable=True)

    def publish_message(self, queue_name: str, message: Any):
        """Publish a message to a queue"""
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                )
            )
            logger.info(f"Message published to queue {queue_name}")
        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            raise

    def consume_messages(self, queue_name: str, callback: Callable):
        """Consume messages from a queue"""
        try:
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback
            )
            logger.info(f"Started consuming from queue {queue_name}")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Failed to consume messages: {str(e)}")
            raise

    def close(self):
        """Close the connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")

# Queue names
QUEUES = {
    'SCRAPE': 'scrape_queue',
    'PREPROCESS': 'preprocess_queue',
    'EMBED': 'embed_queue',
    'STORE': 'store_queue'
} 