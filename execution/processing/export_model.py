import os
import logging
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ModelExport")

def export_model():
    model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    save_dir = os.path.join(os.path.dirname(__file__), "..", "..", ".tmp", "models", "roberta-sentiment-onnx")
    save_dir = os.path.abspath(save_dir)
    
    if os.path.exists(os.path.join(save_dir, "model.onnx")):
        logger.info(f"Model already exists at {save_dir}. Skipping export.")
        return

    logger.info(f"Downloading and exporting {model_name} to ONNX format. This may take a moment...")
    os.makedirs(save_dir, exist_ok=True)
    
    # Download and auto-export to ONNX
    model = ORTModelForSequenceClassification.from_pretrained(model_name, export=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    model.save_pretrained(save_dir)
    tokenizer.save_pretrained(save_dir)
    logger.info(f"Model successfully exported to {save_dir}")

if __name__ == "__main__":
    export_model()
