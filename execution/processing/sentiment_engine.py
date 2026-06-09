import json
import logging
import time
from datetime import datetime
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure Logging first so it's available for the imports
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SentimentEngine")

import nltk
try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    # Ensure VADER lexicon is downloaded
    nltk.download('vader_lexicon', quiet=True)
    logger.info("NLTK VADER Lexicon verified.")
except (ImportError, Exception):
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        logger.info("Standalone vaderSentiment verified.")
    except ImportError:
        logger.error("Neither NLTK nor vaderSentiment is available.")
        logger.info("Attempting to install missing libraries...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "vaderSentiment", "nltk"])
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        logger.info("Libraries installed and verified.")

from kafka import KafkaConsumer, KafkaProducer

class SentimentEngine:
    def __init__(self, bootstrap_servers=['localhost:9092'], standalone=True):
        self.bootstrap_servers = bootstrap_servers
        self.input_topic = 'sentiment_stream'
        self.output_topic = 'sentiment_results'
        self.standalone = standalone
        
        # Initialize Analyzers
        self.analyzer = SentimentIntensityAnalyzer()
        
        from preprocessor import TextPreprocessor
        from transformer_engine import TransformerSentimentEngine
        
        self.preprocessor = TextPreprocessor()
        self.transformer = TransformerSentimentEngine()
        
        if self.standalone:
            # Initialize Kafka Consumer
            self.consumer = KafkaConsumer(
                self.input_topic,
                bootstrap_servers=self.bootstrap_servers,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='sentiment-brain-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            
            # Initialize Kafka Producer
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            logger.info(f"Sentiment Engine initialized in STANDALONE mode. Listening on '{self.input_topic}'...")
        else:
            logger.info("Sentiment Engine initialized in FLINK mode. No Kafka clients created.")

    def get_sentiment_label(self, compound_score):
        """Maps compound score to discrete labels based on SOP thresholds."""
        if compound_score >= 0.05:
            return "POSITIVE"
        elif compound_score <= -0.05:
            return "NEGATIVE"
        else:
            return "NEUTRAL"

    def analyze_layered(self, text):
        """
        Layered inference strategy:
        1. VADER fast-pass
        2. If high confidence (|compound| > 0.7), use VADER
        3. Otherwise, escalate to DistilBERT (deep path)
        """
        vader_scores = self.analyzer.polarity_scores(text)
        compound = vader_scores['compound']
        
        if abs(compound) > 0.7:
            # Fast path (VADER)
            return {
                "label": self.get_sentiment_label(compound),
                "score": compound,
                "engine": "vader"
            }
        else:
            # Deep path (Transformer)
            transformer_result = self.transformer.predict(text)
            transformer_result["engine"] = "transformer"
            return transformer_result

    def process_messages(self):
        """Infinite loop to consume and process messages."""
        try:
            for message in self.consumer:
                try:
                    start_time = time.time()
                    data = message.value
                    
                    if not data or not isinstance(data, dict):
                        logger.warning("Received empty or malformed message. Skipping.")
                        continue

                    # Preprocess data
                    data = self.preprocessor.preprocess(data)
                    if not data:
                        continue
                    
                    text = data['text']
                    msg_id = data['id']
                    lang = data.get('language', 'unknown')

                    # Perform Layered Sentiment Analysis
                    sentiment_result = self.analyze_layered(text)
                    
                    # Compute latency
                    end_time = time.time()
                    processing_time_ms = (end_time - start_time) * 1000

                    # Construct final enriched payload
                    enriched_data = {
                        "id": msg_id,
                        "timestamp": data.get('timestamp', datetime.utcnow().isoformat() + "Z"),
                        "text": text,
                        "topic": data.get('source', 'unknown'),
                        "language": lang,
                        "needs_translation": lang != 'en' and lang != 'unknown',
                        "sentiment": {
                            "label": sentiment_result['label'],
                            "score": sentiment_result['score'],
                            "engine": sentiment_result['engine']
                        },
                        "processing_time_ms": round(processing_time_ms, 2)
                    }

                    
                    # Produce to Results Topic
                    self.producer.send(self.output_topic, value=enriched_data)
                    
                    # High-visibility logging for the Midterm Demo
                    label = sentiment_result['label']
                    score = sentiment_result['score']
                    sentiment_icon = "[+]" if label == "POSITIVE" else "[-]" if label == "NEGATIVE" else "[=]"
                    logger.info(f"[LIVE PULSE] {sentiment_icon} {label:8} | Score: {score:6.2f} | Text: \"{text[:50]}...\"")

                except Exception as msg_err:
                    logger.error(f"Error processing individual message: {msg_err}")
                    continue

        except KeyboardInterrupt:
            logger.info("Engine stopped by user.")
        except Exception as e:
            logger.error(f"Critical error in engine: {e}")
        finally:
            self.consumer.close()
            self.producer.close()

if __name__ == "__main__":
    engine = SentimentEngine()
    engine.process_messages()
