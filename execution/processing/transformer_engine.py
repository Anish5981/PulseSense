import os
import logging
import numpy as np
try:
    import onnxruntime as ort
    from transformers import AutoTokenizer
except ImportError:
    pass  # Handle gracefully if not installed yet

logger = logging.getLogger("TransformerEngine")

def softmax(x):
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e_x / e_x.sum(axis=-1, keepdims=True)

class TransformerSentimentEngine:
    """
    DistilBERT-based sentiment classifier using ONNX Runtime.
    """
    def __init__(self, model_dir=None):
        if model_dir is None:
            model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".tmp", "models", "roberta-sentiment-onnx"))
        
        self.model_dir = model_dir
        self.tokenizer = None
        self.session = None
        
        try:
            # We attempt to use CUDAExecutionProvider if available, otherwise fallback to CPU
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            self.session = ort.InferenceSession(os.path.join(model_dir, "model.onnx"), providers=providers)
            self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
            logger.info("Transformer Engine initialized with ONNX Runtime.")
            
            # Print actual provider used
            active_provider = self.session.get_providers()[0]
            logger.info(f"ONNX active execution provider: {active_provider}")
        except Exception as e:
            logger.error(f"Failed to load ONNX model from {model_dir}. Run export_model.py first. Error: {e}")

    def predict(self, text: str) -> dict:
        if not self.session or not self.tokenizer:
            return {"label": "NEUTRAL", "score": 0.0, "error": "Model not loaded"}

        # Tokenize
        inputs = self.tokenizer(text, return_tensors="np", truncation=True, max_length=512, padding=True)
        
        # ONNX Inference
        ort_inputs = {
            "input_ids": inputs["input_ids"].astype(np.int64),
            "attention_mask": inputs["attention_mask"].astype(np.int64)
        }
        
        ort_outs = self.session.run(None, ort_inputs)
        logits = ort_outs[0]
        
        # Apply softmax to get probabilities
        probs = softmax(logits)[0]
        
        # Twitter-RoBERTa labels: 0 -> NEGATIVE, 1 -> NEUTRAL, 2 -> POSITIVE
        pred_idx = np.argmax(probs)
        labels = ["NEGATIVE", "NEUTRAL", "POSITIVE"]
        label = labels[pred_idx]
        
        # Map score to -1.0 to 1.0 range
        # Positive prob - Negative prob
        score = float(probs[2] - probs[0])
        
        return {
            "label": label,
            "score": score
        }

if __name__ == "__main__":
    engine = TransformerSentimentEngine()
    print(engine.predict("I absolutely love this new technology!"))
    print(engine.predict("This is the worst experience I've ever had."))
