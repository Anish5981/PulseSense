import json
import logging
import time
import os
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
from kafka import KafkaConsumer

# Load Environment Variables
load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DatabaseWriter")

class DatabaseWriter:
    def __init__(self, kafka_bootstrap=['localhost:9092']):
        self.kafka_bootstrap = kafka_bootstrap
        self.topic = 'sentiment_results'
        self.batch_size = 50
        self.batch_wait_time = 2.0  # Seconds
        self.batch = []
        self.last_flush = time.time()
        
        # Database Config
        self.db_params = {
            "dbname": os.getenv("POSTGRES_DB", "pulsesense"),
            "user": os.getenv("POSTGRES_USER", "admin"),
            "password": os.getenv("POSTGRES_PASSWORD", "password"),
            "host": "localhost",
            "port": 5432
        }
        
        # Initialize Kafka Consumer
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.kafka_bootstrap,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='persistence-writer-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        self.conn = None
        self.connect_db()

    def connect_db(self):
        """Attempts to connect to PostgreSQL with retries."""
        while not self.conn:
            try:
                self.conn = psycopg2.connect(**self.db_params)
                logger.info("Connected to TimescaleDB.")
            except Exception as e:
                logger.error(f"Waiting for Database... {e}")
                time.sleep(5)

    def flush_to_db(self):
        """Writes the current batch to the database."""
        if not self.batch:
            return

        try:
            with self.conn.cursor() as cur:
                # Optimized SQL batch insert with conflict handling
                sql = """
                INSERT INTO sentiment_logs 
                (timestamp, tweet_id, text, topic, sentiment_label, sentiment_score, processing_ms)
                VALUES %s
                ON CONFLICT (timestamp, tweet_id) DO NOTHING
                """
                
                # Format data for execute_values
                data_list = [
                    (
                        item['timestamp'],
                        item['id'],
                        item['text'],
                        item['topic'],
                        item['sentiment']['label'],
                        item['sentiment']['score'],
                        item['processing_time_ms']
                    ) for item in self.batch
                ]
                
                execute_values(cur, sql, data_list)
                self.conn.commit()
                
                logger.info(f"💾 Flushed {len(self.batch)} records to database.")
                self.batch = []
                self.last_flush = time.time()
                
        except (psycopg2.InterfaceError, psycopg2.OperationalError) as db_err:
            logger.error(f"Database connection lost: {db_err}")
            self.conn = None
            self.connect_db()
        except Exception as e:
            logger.error(f"Error flushing to DB: {e}")
            self.conn.rollback()

    def run(self):
        """Infinite loop to consume analyzed data."""
        logger.info(f"Writer started. Listening for results on '{self.topic}'...")
        try:
            for message in self.consumer:
                self.batch.append(message.value)
                
                # Check if batch is full or timer expired
                if len(self.batch) >= self.batch_size or (time.time() - self.last_flush) > self.batch_wait_time:
                    self.flush_to_db()
                    
        except KeyboardInterrupt:
            logger.info("Writer stopped by user.")
        finally:
            if self.batch:
                self.flush_to_db()
            self.consumer.close()
            if self.conn:
                self.conn.close()

if __name__ == "__main__":
    writer = DatabaseWriter()
    writer.run()
