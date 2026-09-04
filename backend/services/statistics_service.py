# ==============================================================
# Statistics Service
# ==============================================================
# Thin wrapper around database statistics queries.
# Exists as a separate service for clean architecture —
# if we ever add caching or computed metrics, they go here.
# ==============================================================

from database.models import get_statistics, get_recent_predictions


def get_dashboard_stats() -> dict:
    """Get all dashboard statistics from the database."""
    return get_statistics()


def get_recent(limit: int = 20) -> list[dict]:
    """Get recent predictions for the dashboard table."""
    return get_recent_predictions(limit)
