# ==============================================================
# Database Models — CRUD Operations for Predictions
# ==============================================================
# All database read/write operations are centralized here.
# The rest of the application uses these functions instead
# of writing raw SQL.
# ==============================================================

import logging
from database.database import get_connection

logger = logging.getLogger(__name__)


def save_prediction(data: dict) -> int:
    """
    Save a prediction to the database.

    Args:
        data: {
            "predicted_class": "freshbanana",
            "fruit": "Banana",
            "condition": "Fresh/Ripe",
            "confidence": 96.42,
            "servo_angle": 120,
            "destination": "Ripe Bin",
            "arduino_command": "120",
            "sorting_status": "COMMAND_SENT"
        }

    Returns:
        The ID of the newly inserted row.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO predictions
                (predicted_class, fruit, condition, confidence,
                 servo_angle, destination, arduino_command, sorting_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["predicted_class"],
                data["fruit"],
                data["condition"],
                data["confidence"],
                data.get("servo_angle"),
                data.get("destination"),
                data.get("arduino_command"),
                data.get("sorting_status", "PENDING"),
            ),
        )
        conn.commit()
        prediction_id = cursor.lastrowid
        logger.info(f"Saved prediction #{prediction_id}: {data['fruit']} - {data['condition']}")
        return prediction_id
    except Exception as e:
        logger.error(f"Failed to save prediction: {e}", exc_info=True)
        raise
    finally:
        conn.close()


def update_sorting_status(prediction_id: int, status: str):
    """Update the sorting status of a prediction (e.g., COMMAND_SENT → SORTED)."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE predictions SET sorting_status = ? WHERE id = ?",
            (status, prediction_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_prediction(prediction_id: int) -> bool:
    """Delete a prediction from the database by ID."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM predictions WHERE id = ?",
            (prediction_id,),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_recent_predictions(limit: int = 20) -> list[dict]:
    """Get the most recent predictions, newest first."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM predictions ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_all_predictions() -> list[dict]:
    """Get all predictions (for statistics calculation)."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM predictions ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_statistics() -> dict:
    """
    Calculate statistics from all stored predictions.

    Returns:
        {
            "total_fruits": 42,
            "apples": 15, "bananas": 14, "oranges": 13,
            "fresh": 18, "unripe": 14, "rotten": 10,
            "average_confidence": 96.4,
            "sorting_success": 97.2
        }
    """
    conn = get_connection()
    try:
        # Total count
        total = conn.execute("SELECT COUNT(*) as cnt FROM predictions").fetchone()["cnt"]

        if total == 0:
            return {
                "total_fruits": 0,
                "apples": 0,
                "bananas": 0,
                "oranges": 0,
                "fresh": 0,
                "unripe": 0,
                "rotten": 0,
                "average_confidence": 0.0,
                "sorting_success": 0.0,
            }

        # Per-fruit counts
        apples = conn.execute(
            "SELECT COUNT(*) as cnt FROM predictions WHERE fruit = 'Apple'"
        ).fetchone()["cnt"]
        bananas = conn.execute(
            "SELECT COUNT(*) as cnt FROM predictions WHERE fruit = 'Banana'"
        ).fetchone()["cnt"]
        oranges = conn.execute(
            "SELECT COUNT(*) as cnt FROM predictions WHERE fruit = 'Orange'"
        ).fetchone()["cnt"]

        # Per-condition counts
        fresh = conn.execute(
            "SELECT COUNT(*) as cnt FROM predictions WHERE condition = 'Fresh/Ripe'"
        ).fetchone()["cnt"]
        unripe = conn.execute(
            "SELECT COUNT(*) as cnt FROM predictions WHERE condition = 'Unripe'"
        ).fetchone()["cnt"]
        rotten = conn.execute(
            "SELECT COUNT(*) as cnt FROM predictions WHERE condition = 'Rotten'"
        ).fetchone()["cnt"]

        # Average confidence
        avg_conf = conn.execute(
            "SELECT AVG(confidence) as avg FROM predictions"
        ).fetchone()["avg"]

        # Sorting success = predictions where sorting completed or was simulated successfully
        sorted_count = conn.execute(
            "SELECT COUNT(*) as cnt FROM predictions WHERE sorting_status IN ('SORTED', 'SIMULATED', 'COMMAND_SENT', 'SUCCESS')"
        ).fetchone()["cnt"]

        sorting_success = (sorted_count / total * 100) if total > 0 else 0.0

        return {
            "total_fruits": total,
            "apples": apples,
            "bananas": bananas,
            "oranges": oranges,
            "fresh": fresh,
            "unripe": unripe,
            "rotten": rotten,
            "average_confidence": round(avg_conf, 2) if avg_conf else 0.0,
            "sorting_success": round(sorting_success, 2),
        }
    finally:
        conn.close()
