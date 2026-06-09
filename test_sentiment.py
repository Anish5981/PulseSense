import sys
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sys.path.append('c:/Users/91620/Desktop/Code/pulseApp/execution/processing')
from transformer_engine import TransformerSentimentEngine

analyzer = SentimentIntensityAnalyzer()
transformer = TransformerSentimentEngine()

texts = [
    "> wouldn't change anything",
    "[delayed]",
    "i would do the same for my children ~ however children have a special ability to revolt against any arbitrary constraints provided by parents, community, society. it differs person to person of course."
]

for text in texts:
    vader = analyzer.polarity_scores(text)
    trans = transformer.predict(text)
    print(f"Text: {text}")
    print(f"VADER: {vader}")
    print(f"Transformer: {trans}")
    print("-" * 50)
