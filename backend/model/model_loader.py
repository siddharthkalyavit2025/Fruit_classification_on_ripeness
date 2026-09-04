# ==============================================================
# Model Loader — Build EfficientNetV2-S + Load Trained Weights
# ==============================================================
# This module reconstructs the EXACT same architecture used
# during training, then loads the .weights.h5 file.
#
# Architecture:
#   EfficientNetV2-S (pretrained base, include_top=False)
#       ↓
#   GlobalAveragePooling2D
#       ↓
#   BatchNormalization
#       ↓
#   Dense(256, relu)
#       ↓
#   Dropout(0.30)
#       ↓
#   Dense(9, softmax)
#
# The model is loaded ONCE at application startup and kept
# in memory for all subsequent prediction requests.
# ==============================================================

import os
import logging
import tensorflow as tf
from tensorflow import keras
from config import MODEL_WEIGHTS_PATH, MODEL_INPUT_SIZE, NUM_CLASSES

logger = logging.getLogger(__name__)

# Module-level model reference (singleton pattern)
_model = None
_model_status = "not_loaded"


def build_model() -> keras.Model:
    """
    Reconstruct the exact EfficientNetV2-S architecture
    that was used during training.
    """
    # Base model — EfficientNetV2-S without classification head
    base_model = keras.applications.EfficientNetV2S(
        include_top=False,
        weights=None,  # We'll load our trained weights, not ImageNet
        input_shape=(*MODEL_INPUT_SIZE, 3),
    )

    # Build the custom classification head
    model = keras.Sequential([
        base_model,
        keras.layers.GlobalAveragePooling2D(),
        keras.layers.BatchNormalization(),
        keras.layers.Dense(256, activation="relu"),
        keras.layers.Dropout(0.30),
        keras.layers.Dense(NUM_CLASSES, activation="softmax"),
    ])

    # Compile (required before loading weights in some Keras versions)
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model


def load_model() -> bool:
    """
    Build the model architecture and load the trained weights.
    Called once at application startup.

    Returns:
        True if model loaded successfully, False otherwise.
    """
    global _model, _model_status

    weights_path = os.path.abspath(MODEL_WEIGHTS_PATH)
    logger.info(f"Loading model weights from: {weights_path}")

    if not os.path.exists(weights_path):
        logger.error(f"Model weights file not found: {weights_path}")
        _model_status = "error"
        return False

    try:
        # Step 1: Build architecture
        logger.info("Building EfficientNetV2-S architecture...")
        _model = build_model()

        # Step 2: Load trained weights
        logger.info("Loading trained weights...")
        _model.load_weights(weights_path)

        # Step 3: Warm up with a dummy prediction
        # This initializes internal TF buffers so the first real
        # prediction isn't slow.
        import numpy as np
        dummy = np.zeros((1, *MODEL_INPUT_SIZE, 3), dtype=np.float32)
        _model.predict(dummy, verbose=0)

        _model_status = "ready"
        logger.info("✅ Model loaded successfully and warmed up!")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}", exc_info=True)
        _model_status = "error"
        _model = None
        return False


def get_model() -> keras.Model | None:
    """Get the loaded model instance."""
    return _model


def get_model_status() -> str:
    """Get current model status: 'ready', 'not_loaded', or 'error'."""
    return _model_status
