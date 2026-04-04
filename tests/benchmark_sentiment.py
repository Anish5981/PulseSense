import os
import sys
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Ensure the VADER lexicon is available
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

class SentimentBenchmark:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        
        # --- TEST DATASET (Ground Truth) ---
        self.test_cases = [
            # Positive Cases
            ("I love the new PulseSense platform, it's incredibly fast!", "POSITIVE"),
            ("The best sentiment engine I've ever used. Great job!", "POSITIVE"),
            ("Everything is working perfectly and I'm very happy.", "POSITIVE"),
            ("This is a game changer for real-time analytics.", "POSITIVE"),
            ("The support is outstanding and very helpful.", "POSITIVE"),
            
            # Negative Cases
            ("I hate when the system crashes during a live stream.", "NEGATIVE"),
            ("The latency is unacceptable, we need better performance.", "NEGATIVE"),
            ("This update is terrible and broke my existing workflow.", "NEGATIVE"),
            ("I'm extremely disappointed with the service quality.", "NEGATIVE"),
            ("The documentation is confusing and hard to follow.", "NEGATIVE"),
            
            # Neutral Cases
            ("The system version 1.0 has been deployed to test.", "NEUTRAL"),
            ("The meeting is scheduled for tomorrow at 2 PM.", "NEUTRAL"),
            ("Kafka is running on port 9092.", "NEUTRAL"),
            ("New healthcare regulations were announced this morning.", "NEUTRAL"),
            ("Checking out the technical specifications for the GPU.", "NEUTRAL"),
            
            # Sarcasm / Nuance (Challenging)
            ("Oh great, another error. Just what I wanted.", "NEGATIVE"),
            ("Wow, amazing system. My car won't even start now.", "NEGATIVE"),
            ("Yeah, because waiting 40 minutes for pizza is 'optimal'.", "NEGATIVE"),
            
            # Mixed Emotions
            ("The screen is beautiful but the battery life is awful.", "NEGATIVE"),
            ("I like the features, but the price is too high.", "NEUTRAL"),
            
            # Negation
            ("It wasn't that bad actually, I kind of liked it.", "POSITIVE"),
            ("I don't think I can trust these metrics anymore.", "NEGATIVE"),
            
            # Context / Slang
            ("PulseSense is fire! Best dev tool of 2026.", "POSITIVE"),
            ("This project is a total disaster, avoid at all costs.", "NEGATIVE")
        ]

    def get_label(self, score):
        if score >= 0.05: return "POSITIVE"
        if score <= -0.05: return "NEGATIVE"
        return "NEUTRAL"

    def run_benchmark(self):
        print("\n--- PulseSense Sentiment Audit ---")
        print(f"Testing {len(self.test_cases)} scenarios...\n")
        
        correct = 0
        mistakes = []
        
        for text, ground_truth in self.test_cases:
            scores = self.sia.polarity_scores(text)
            compound = scores['compound']
            prediction = self.get_label(compound)
            
            if prediction == ground_truth:
                correct += 1
                status = "✅"
            else:
                status = "❌"
                mistakes.append({
                    "text": text,
                    "expected": ground_truth,
                    "got": prediction,
                    "score": compound
                })
            
            print(f"[{status}] {text[:50]:<50} | Exp: {ground_truth:<8} | Got: {prediction}")

        accuracy = (correct / len(self.test_cases)) * 100
        print(f"\n--- Final Results ---")
        print(f"Total Accuracy: {accuracy:.2f}%")
        
        if mistakes:
            print(f"\nCritical Insights (Where we failed):")
            for m in mistakes:
                print(f"🚨 Text: '{m['text']}'")
                print(f"   Expected: {m['expected']} | Predicted: {m['got']} (Score: {m['score']})")
        
        return accuracy

if __name__ == "__main__":
    bench = SentimentBenchmark()
    bench.run_benchmark()
