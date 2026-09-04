# ==============================================================
# Prediction Service — Orchestration Layer
# ==============================================================
# This is the main orchestration service that ties everything
# together for a prediction request:
#
#   Image → Predict → Sort → Save → Arduino → Return Result
#
# It calls the individual modules (predictor, sorting, serial,
# database) in the correct order.
# ==============================================================

import logging
from model.predictor import predict_image
from hardware.sorting_service import get_sorting_action
from hardware.serial_service import serial_service
from database.models import save_prediction, update_sorting_status

logger = logging.getLogger(__name__)


def process_prediction(image_bytes: bytes) -> dict:
    """
    Full prediction pipeline:
        1. Run AI inference
        2. Determine sorting action
        3. Save to database
        4. Send command to Arduino
        5. Return complete result

    Args:
        image_bytes: Raw image bytes from the uploaded file

    Returns:
        Complete prediction result with sorting info.
    """
    # ----- Step 1: AI Inference -----
    prediction = predict_image(image_bytes)

    if not prediction["success"]:
        return prediction  # Return error as-is

    # ----- Step 2: Sorting Decision -----
    sorting = get_sorting_action(prediction["condition"])

    # ----- Step 3: Save to Database -----
    db_data = {
        "predicted_class": prediction["predicted_class"],
        "fruit": prediction["fruit"],
        "condition": prediction["condition"],
        "confidence": prediction["confidence"],
        "servo_angle": sorting["servo_angle"],
        "destination": sorting["destination"],
        "arduino_command": sorting["arduino_command"],
        "sorting_status": "PENDING",
    }

    prediction_id = save_prediction(db_data)

    # ----- Step 4: Send to Arduino -----
    arduino_result = serial_service.send_angle(
        angle=sorting["servo_angle"],
        prediction_id=prediction_id,
    )

    # Update sorting status based on Arduino response
    if arduino_result["success"]:
        sorting_status = "SORTED"
    elif not serial_service.is_connected:
        sorting_status = "SIMULATED"
    else:
        sorting_status = "ARDUINO_ERROR"

    update_sorting_status(prediction_id, sorting_status)

    # ----- Step 5: Return Complete Result -----
    return {
        "success": True,
        "prediction_id": prediction_id,
        "predicted_class": prediction["predicted_class"],
        "fruit": prediction["fruit"],
        "condition": prediction["condition"],
        "emoji": prediction["emoji"],
        "confidence": prediction["confidence"],
        "class_index": prediction["class_index"],
        "destination": sorting["destination"],
        "servo_angle": sorting["servo_angle"],
        "arduino_command": sorting["arduino_command"],
        "sorting_status": sorting_status,
        "arduino_response": arduino_result.get("response", ""),
        "all_probabilities": prediction.get("all_probabilities", {}),
    }
