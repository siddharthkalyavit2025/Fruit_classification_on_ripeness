# ==============================================================
# Class Mapping — 9-class → fruit + condition
# ==============================================================
# This module provides a single source of truth for converting
# the model's integer output index into human-readable info.
# ==============================================================

from config import CLASS_NAMES, CLASS_INFO


def get_class_name(index: int) -> str:
    """Convert model output index (0-8) to class name string."""
    if 0 <= index < len(CLASS_NAMES):
        return CLASS_NAMES[index]
    raise ValueError(f"Invalid class index: {index}. Expected 0-{len(CLASS_NAMES) - 1}")


def get_class_info(class_name: str) -> dict:
    """
    Get human-readable info for a class name.

    Returns:
        {
            "fruit": "Banana",
            "condition": "Fresh/Ripe",
            "emoji": "🍌"
        }
    """
    if class_name in CLASS_INFO:
        return CLASS_INFO[class_name].copy()
    raise ValueError(f"Unknown class name: {class_name}")


def parse_prediction(index: int) -> dict:
    """
    Combine index → class name → human-readable info in one call.

    Returns:
        {
            "predicted_class": "freshbanana",
            "fruit": "Banana",
            "condition": "Fresh/Ripe",
            "emoji": "🍌"
        }
    """
    class_name = get_class_name(index)
    info = get_class_info(class_name)
    return {
        "predicted_class": class_name,
        **info,
    }
