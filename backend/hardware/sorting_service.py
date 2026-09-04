# ==============================================================
# Hardware Service — Maps AI Prediction to Sorting Action
# ==============================================================
# Given a predicted condition (Fresh/Ripe, Rotten, Unripe),
# determines the sorting destination, servo angle, and
# Arduino command.
#
# All sorting configuration comes from config.SORTING_MAP.
# Change servo angles in ONE place: config.py
# ==============================================================

import logging
from config import SORTING_MAP

logger = logging.getLogger(__name__)


def get_sorting_action(condition: str) -> dict:
    """
    Determine sorting action based on fruit condition.

    Args:
        condition: "Fresh/Ripe", "Rotten", or "Unripe"

    Returns:
        {
            "destination": "Ripe Bin",
            "servo_angle": 120,
            "arduino_command": "120"    ← the angle as string (Arduino protocol)
        }
    """
    if condition not in SORTING_MAP:
        logger.warning(f"Unknown condition: {condition}")
        return {
            "destination": "Unknown",
            "servo_angle": 90,          # Default center
            "arduino_command": "90",
        }

    mapping = SORTING_MAP[condition]

    return {
        "destination": mapping["destination"],
        "servo_angle": mapping["servo_angle"],
        # Arduino expects a plain integer angle as string
        "arduino_command": str(mapping["servo_angle"]),
    }
