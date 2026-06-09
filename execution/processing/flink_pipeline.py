import json
import logging
import time
from datetime import datetime

from pyflink.common import Types, WatermarkStrategy, SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaSink, KafkaRecordSerializationSchema, KafkaOffsetsInitializer
from pyflink.datastream.functions import MapFunction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FlinkPipeline")

class SentimentProcessor(MapFunction):
    def open(self, runtime_context):
        import sys
        import os
        # Add the pulseApp path so we can import our modules
        sys.path.append("/opt/pulse")
        from execution.processing.sentiment_engine import SentimentEngine
        
        # Initialize engine in Flink mode (no Kafka clients)
        self.engine = SentimentEngine(standalone=False)

    def map(self, value):
        start_time = time.time()
        
        try:
            data = json.loads(value)
            
            # Preprocess
            data = self.engine.preprocessor.preprocess(data)
            if not data:
                return "" # Filtered out
                
            text = data['text']
            msg_id = data['id']
            lang = data.get('language', 'unknown')

            # Analyze
            sentiment_result = self.engine.analyze_layered(text)
            
            # Compute latency
            processing_time_ms = (time.time() - start_time) * 1000

            # Construct final enriched payload
            enriched_data = {
                "id": msg_id,
                "timestamp": data.get('timestamp', datetime.utcnow().isoformat() + "Z"),
                "text": text,
                "topic": data.get('source', 'unknown'),
                "language": lang,
                "sentiment": {
                    "label": sentiment_result['label'],
                    "score": sentiment_result['score'],
                    "engine": sentiment_result['engine']
                },
                "processing_time_ms": round(processing_time_ms, 2)
            }
            return json.dumps(enriched_data)
            
        except Exception as e:
            logger.error(f"Error processing message in Flink map function: {e}")
            return ""

def build_pipeline():
    env = StreamExecutionEnvironment.get_execution_environment()
    
    # In Flink 1.18, we can just use the SimpleStringSchema for JSON
    
    # 1. Kafka Source
    kafka_source = KafkaSource.builder() \
        .set_topics("sentiment_stream") \
        .set_bootstrap_servers("kafka:29092") \
        .set_group_id("flink-sentiment-group") \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()
        
    stream = env.from_source(
        kafka_source, 
        WatermarkStrategy.no_watermarks(), 
        "kafka-sentiment-source"
    )
    
    # 2. Process (Preprocess + Analyze)
    # We use a FlatMap equivalent by filtering out empty strings returned by map
    processed_stream = stream.map(SentimentProcessor(), Types.STRING()) \
                             .filter(lambda x: len(x) > 0)
    
    # 3. Kafka Sink
    record_serializer = KafkaRecordSerializationSchema.builder() \
        .set_topic("sentiment_results") \
        .set_value_serialization_schema(SimpleStringSchema()) \
        .build()
        
    kafka_sink = KafkaSink.builder() \
        .set_record_serializer(record_serializer) \
        .set_bootstrap_servers("kafka:29092") \
        .build()
        
    processed_stream.sink_to(kafka_sink)
    
    env.execute("PulseSense-Sentiment-Pipeline")

if __name__ == "__main__":
    build_pipeline()
