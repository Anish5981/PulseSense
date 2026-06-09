import json
import logging
import psycopg2
from kafka import KafkaConsumer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("StandaloneSink")

class TimescaleDBSink:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'sentiment_results',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='timescaledb-writer-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        # Connect to TimescaleDB
        self.conn = psycopg2.connect(
            dbname='pulsesense',
            user='admin',
            password='pulsesense_secure_pass',
            host='localhost',
            port='5432'
        )
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()
        logger.info("Connected to TimescaleDB. Listening for results...")

    def run(self):
        try:
            for message in self.consumer:
                data = message.value
                try:
                    # Insert into sentiment_logs
                    self.cursor.execute(
                        """
                        INSERT INTO sentiment_logs (timestamp, tweet_id, text, topic, sentiment_label, sentiment_score, processing_ms)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (timestamp, tweet_id) DO NOTHING;
                        """,
                        (
                            data['timestamp'],
                            data['id'],
                            data['text'],
                            data['topic'],
                            data['sentiment']['label'],
                            data['sentiment']['score'],
                            data['processing_time_ms']
                        )
                    )
                    logger.info(f"Saved to DB: {data['id']} [{data['sentiment']['label']}]")
                except Exception as e:
                    logger.error(f"Error saving to DB: {e}")
        except KeyboardInterrupt:
            logger.info("Shutting down sink...")
        finally:
            self.cursor.close()
            self.conn.close()
            self.consumer.close()

if __name__ == '__main__':
    sink = TimescaleDBSink()
    sink.run()
