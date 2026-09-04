# ==============================================================
# Pydantic Schemas — API Request/Response Models
# ==============================================================
# These define the exact shape of API responses so that:
#   1. The API docs (Swagger) are accurate
#   2. Responses are validated automatically
#   3. The React frontend knows exactly what to expect
# ==============================================================

from pydantic import BaseModel
from typing import Optional


class PredictionResponse(BaseModel):
    """Response from POST /predict"""
    success: bool
    prediction_id: Optional[int] = None
    predicted_class: Optional[str] = None
    fruit: Optional[str] = None
    condition: Optional[str] = None
    emoji: Optional[str] = None
    confidence: Optional[float] = None
    class_index: Optional[int] = None
    destination: Optional[str] = None
    servo_angle: Optional[int] = None
    current_servo_angle: Optional[int] = 0
    arduino_command: Optional[str] = None
    arduino_status: Optional[str] = None
    sorting_status: Optional[str] = None
    arduino_response: Optional[str] = None
    all_probabilities: Optional[dict] = None
    error: Optional[str] = None


class StatsResponse(BaseModel):
    """Response from GET /stats"""
    total_fruits: int = 0
    apples: int = 0
    bananas: int = 0
    oranges: int = 0
    fresh: int = 0
    unripe: int = 0
    rotten: int = 0
    average_confidence: float = 0.0
    sorting_success: float = 0.0


class StatusResponse(BaseModel):
    """Response from GET /status"""
    camera: str = "unknown"
    model: str = "unknown"
    arduino: str = "unknown"
    servo: str = "unknown"
    serial_port: Optional[str] = None
    current_servo_angle: Optional[int] = 0
    available_ports: Optional[list] = None


class SystemInfoResponse(BaseModel):
    """Response from GET /system-info (CPU, MEM, GPU stats for sidebar)"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    gpu_percent: Optional[float] = None
    gpu_available: bool = False
