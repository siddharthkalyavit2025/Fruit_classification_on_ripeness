# ==============================================================
# Predictor — Image Preprocessing + Model Inference
# ==============================================================
# Takes raw image bytes → preprocesses → runs through model
# → returns predicted class index + confidence.
#
# Preprocessing matches EfficientNetV2 expectations:
#   1. Decode image to RGB
#   2. Resize to 224 × 224
#   3. Apply EfficientNetV2 preprocessing (scales to [-1, 1])
# ==============================================================

import logging
import numpy as np
from PIL import Image
import io
import tensorflow as tf
from config import MODEL_INPUT_SIZE
from model.model_loader import get_model, get_model_status
from model.class_mapping import parse_prediction

logger = logging.getLogger(__name__)


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Convert raw image bytes into the tensor format expected by
    EfficientNetV2-S.

    Steps:
        1. Decode bytes → PIL Image
        2. Convert to RGB (handles RGBA, grayscale, etc.)
        3. Resize to 224 × 224
        4. Convert to numpy float32 array
        5. Apply EfficientNetV2 preprocessing
        6. Add batch dimension → shape (1, 224, 224, 3)

    Returns:
        numpy array of shape (1, 224, 224, 3)
    """
    # Decode image
    image = Image.open(io.BytesIO(image_bytes))

    # Ensure RGB (handles RGBA, grayscale, palette images)
    image = image.convert("RGB")

    # Resize to model input size
    image = image.resize(MODEL_INPUT_SIZE, Image.LANCZOS)

    # Convert to numpy array — shape (224, 224, 3), dtype uint8, values [0, 255]
    img_array = np.array(image, dtype=np.float32)

    # Apply EfficientNetV2 preprocessing
    # This scales pixel values from [0, 255] to [-1, 1]
    img_array = tf.keras.applications.efficientnet_v2.preprocess_input(img_array)

    # Add batch dimension → (1, 224, 224, 3)
    img_array = np.expand_dims(img_array, axis=0)

    return img_array


def predict_image(image_bytes: bytes) -> dict:
    """
    Run a full prediction on raw image bytes.

    Returns:
        {
            "success": True,
            "predicted_class": "freshbanana",
            "fruit": "Banana",
            "condition": "Fresh/Ripe",
            "emoji": "🍌",
            "confidence": 96.42,
            "class_index": 1,
            "all_probabilities": { "freshapples": 0.3, ... }
        }
        or
        {
            "success": False,
            "error": "Model not loaded"
        }
    """
    # Check model is ready
    model = get_model()
    if model is None:
        return {
            "success": False,
            "error": f"Model not available (status: {get_model_status()})"
        }

    try:
        # Preprocess
        img_tensor = preprocess_image(image_bytes)

        # Run inference
        predictions = model.predict(img_tensor, verbose=0)

        # predictions shape: (1, 9) — one row of 9 softmax probabilities
        probabilities = predictions[0]

        # Get the winning class
        class_index = int(np.argmax(probabilities))
        confidence = float(probabilities[class_index]) * 100  # as percentage

        # Parse into human-readable info
        result = parse_prediction(class_index)

        # Build all probabilities dict for debugging / detailed view
        from config import CLASS_NAMES
        all_probs = {
            name: round(float(prob) * 100, 2)
            for name, prob in zip(CLASS_NAMES, probabilities)
        }

        return {
            "success": True,
            **result,
            "confidence": round(confidence, 2),
            "class_index": class_index,
            "all_probabilities": all_probs,
        }

    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }
