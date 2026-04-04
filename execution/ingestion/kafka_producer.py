import json
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PulseProducer")

class PulseProducer:
    """
    A robust Kafka Producer for the PulseSense platform.
    Handles JSON serialization and asynchronous delivery.
    """
    def __init__(self, bootstrap_servers=['localhost:9092']):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks=1,
                compression_type='gzip',
                retries=5
            )
            logger.info(f"Connected to Kafka at {bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise

    def send_message(self, topic, message):
        """
        Sends a message to the specified Kafka topic.
        """
        try:
            future = self.producer.send(topic, message)
            # We don't block here for maximum throughput
            future.add_callback(self._on_success)
            future.add_errback(self._on_error)
        except KafkaError as e:
            logger.error(f"Error sending message: {e}")

    def _on_success(self, record_metadata):
        # logging every single message might be too noisy at high volume
        # logger.debug(f"Message sent to {record_metadata.topic} partition {record_metadata.partition}")
        pass

    def _on_error(self, excp):
        logger.error(f"Message delivery failed: {excp}")

    def flush(self):
        """
        Ensure all messages are delivered.
        """
        self.producer.flush()

    def close(self):
        """
        Close the producer connection.
        """
        self.producer.close()

if __name__ == "__main__":
    # Quick self-test
    test_producer = PulseProducer()
    test_producer.send_message('sentiment_stream', {"test": "connection", "status": "ok"})
    test_producer.flush()
    print("Test message sent successfully.")
