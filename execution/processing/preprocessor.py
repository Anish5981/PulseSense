import re
import html
import logging
try:
    from langdetect import detect
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "langdetect"])
    from langdetect import detect

logger = logging.getLogger("TextPreprocessor")

class TextPreprocessor:
    def __init__(self):
        # In a real distributed system, we would use Redis or a Bloom filter.
        # For this prototype, a simple in-memory set is used.
        self.seen_ids = set()
        
    def is_duplicate(self, msg_id: str) -> bool:
        if msg_id in self.seen_ids:
            return True
        self.seen_ids.add(msg_id)
        # Prevent memory leak in long-running processes
        if len(self.seen_ids) > 100000:
            self.seen_ids.clear()
        return False

    def clean_html(self, text: str) -> str:
        """Remove HTML tags, URLs, and decode HTML entities."""
        # Decode HTML entities (e.g., &amp; -> &)
        text = html.unescape(text)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        return text

    def normalize(self, text: str) -> str:
        """Normalize text by converting to lowercase and stripping extra spaces."""
        text = text.lower()
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def detect_language(self, text: str) -> str:
        """Detect the language of the text. Returns 'unknown' if detection fails."""
        try:
            return detect(text)
        except Exception:
            return 'unknown'

    def preprocess(self, data: dict) -> dict:
        """
        Full pipeline: dedup → clean → normalize → detect_language.
        Returns None if message should be filtered (e.g. duplicate or empty).
        """
        msg_id = data.get('id') or data.get('message_id') or data.get('metadata', {}).get('hn_id') or 'unknown_id'
        
        if msg_id != 'unknown_id' and self.is_duplicate(msg_id):
            return None

        text = data.get('text') or data.get('content') or ''
        
        text = self.clean_html(text)
        text = self.normalize(text)
        
        if not text:
            return None
            
        lang = self.detect_language(text)
        
        # We attach language to the data and update text
        data['text'] = text
        data['language'] = lang
        data['id'] = msg_id  # Normalize ID field
        return data

if __name__ == "__main__":
    # Test the preprocessor
    pp = TextPreprocessor()
    test_data = {
        'id': '123',
        'text': 'Hello <b>world</b>! Check out https://example.com &amp; enjoy.'
    }
    print(pp.preprocess(test_data))
