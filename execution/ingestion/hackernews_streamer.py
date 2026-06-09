import requests
import time
import logging
from datetime import datetime
from kafka_producer import PulseProducer
from backoff import exponential_backoff

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HackerNewsStreamer")

HN_API = "https://hacker-news.firebaseio.com/v0"

class HackerNewsStreamer:
    def __init__(self, tps=5):
        self.producer = PulseProducer()
        self.tps = tps
    
    def _fetch_item(self, item_id, max_retries=3):
        """Fetch a single HN item (story/comment) by ID with retries."""
        for attempt in range(max_retries):
            try:
                resp = requests.get(f"{HN_API}/item/{item_id}.json", timeout=5)
                if resp.ok:
                    return resp.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Error fetching item {item_id}: {e}")
                
            delay = exponential_backoff(attempt)
            time.sleep(delay)
        return None
    
    def stream_new_comments(self):
        """Poll /maxitem and fetch new comments continuously."""
        logger.info("Starting Hacker News Streamer...")
        try:
            max_id_resp = requests.get(f"{HN_API}/maxitem.json")
            if not max_id_resp.ok:
                logger.error("Failed to get initial maxitem from HN.")
                return
            max_id = max_id_resp.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to HN: {e}")
            return
            
        while True:
            try:
                current_max_resp = requests.get(f"{HN_API}/maxitem.json", timeout=5)
                if current_max_resp.ok:
                    current_max = current_max_resp.json()
                    for item_id in range(max_id + 1, current_max + 1):
                        item = self._fetch_item(item_id)
                        if item and item.get('type') == 'comment' and item.get('text'):
                            # Create payload
                            payload = {
                                "timestamp": datetime.utcfromtimestamp(item['time']).isoformat() + "Z",
                                "user_id": item.get('by', 'anonymous'),
                                "text": item['text'],
                                "source": "hackernews",
                                "metadata": {
                                    "hn_id": item['id'],
                                    "parent_id": item.get('parent'),
                                    "type": item['type']
                                }
                            }
                            self.producer.send_message('sentiment_stream', payload)
                    max_id = current_max
            except requests.exceptions.RequestException as e:
                logger.warning(f"Error checking for new items: {e}")
                time.sleep(exponential_backoff(1)) # Backoff on failure
                
            time.sleep(1.0 / self.tps)

if __name__ == "__main__":
    streamer = HackerNewsStreamer(tps=5)
    try:
        streamer.stream_new_comments()
    except KeyboardInterrupt:
        logger.info("Streamer stopped by user.")
    finally:
        streamer.producer.close()
