# ==============================================================
# Smart Fruit Sorting System — FastAPI Application
# ==============================================================
# This is the main entry point for the backend server.
#
# Startup:
#   1. Load EfficientNetV2-S model (once)
#   2. Initialize SQLite database
#   3. Optionally connect to Arduino
#
# Endpoints:
#   POST /predict         — Upload image → AI prediction + sorting
#   GET  /predictions     — Recent prediction history
#   GET  /stats           — Dashboard statistics
#   GET  /status          — System status (camera, model, arduino)
#   GET  /system-info     — CPU, MEM, GPU stats for sidebar
#   POST /serial/connect  — Connect to Arduino
#   POST /serial/disconnect — Disconnect Arduino
#   GET  /serial/ports    — List available COM ports
#
# Run with:
#   cd backend
#   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
# ==============================================================

import logging
import sys
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Add backend dir to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CORS_ORIGINS, SERIAL_PORT, SERIAL_ENABLED
from model.model_loader import load_model, get_model_status
from database.database import init_database
from services.prediction_service import process_prediction
from hardware.serial_service import serial_service
from services.statistics_service import get_dashboard_stats, get_recent
from schemas.prediction import (
    PredictionResponse,
    StatsResponse,
    StatusResponse,
    SystemInfoResponse,
)

# ---- Logging Setup ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("fruitsort")


# ==============================================================
# Application Lifespan — Startup & Shutdown
# ==============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once at startup and shutdown.
    - Startup: load model, init database, connect Arduino
    - Shutdown: disconnect Arduino
    """
    logger.info("=" * 60)
    logger.info("  Smart Fruit Sorting System — Starting Up")
    logger.info("=" * 60)

    # 1. Initialize database
    init_database()

    # 2. Load AI model (this takes ~10-20 seconds)
    logger.info("Loading EfficientNetV2-S model...")
    model_loaded = load_model()
    if model_loaded:
        logger.info("Model loaded successfully!")
    else:
        logger.error("Model failed to load! Predictions will not work.")

    # 3. Connect to Arduino (optional — won't block if not connected)
    if SERIAL_ENABLED:
        logger.info(f"Attempting to connect to Arduino on {SERIAL_PORT}...")
        connected = serial_service.connect()
        if connected:
            logger.info("Arduino connected!")
        else:
            logger.warning("Arduino not connected. Sorting commands will fail.")
    else:
        logger.info("Serial communication is DISABLED in config")

    logger.info("=" * 60)
    logger.info("  System Ready! Open http://localhost:8000/docs for API docs")
    logger.info("=" * 60)

    yield  # ← Application runs here

    # Shutdown
    logger.info("Shutting down...")
    serial_service.disconnect()
    logger.info("Goodbye!")


# ==============================================================
# FastAPI App
# ==============================================================
app = FastAPI(
    title="Smart Fruit Sorting System",
    description="AI-powered fruit classification and sorting with Arduino integration",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================
# Endpoints
# ==============================================================

@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    """
    Upload a fruit image for AI classification and sorting.

    1. Receives image file
    2. Runs EfficientNetV2-S inference
    3. Determines sorting destination
    4. Saves to database
    5. Sends command to Arduino
    6. Returns complete result
    """
    # Validate file
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Please upload an image.",
        )

    # Read image bytes
    image_bytes = await file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    logger.info(f"Received image: {file.filename} ({len(image_bytes)} bytes)")

    # Run full prediction pipeline
    result = process_prediction(image_bytes)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Prediction failed"))

    return result


@app.get("/predictions")
async def get_predictions(limit: int = 20):
    """Get recent predictions for the dashboard table."""
    predictions = get_recent(limit)
    return {"predictions": predictions}


@app.delete("/predictions/{prediction_id}")
async def remove_prediction(prediction_id: int):
    """Delete a prediction from history and recalculate stats."""
    from database.models import delete_prediction
    deleted = delete_prediction(prediction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return {"success": True, "message": f"Prediction #{prediction_id} deleted successfully"}


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get dashboard statistics calculated from actual prediction data."""
    return get_dashboard_stats()


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Get live system status.
    All values come from actual component states, never hard-coded.
    """
    model_status = get_model_status()
    arduino_status = serial_service.status

    # Servo status is derived from Arduino status
    servo_status = "ready" if arduino_status == "connected" else "unavailable"

    return {
        "camera": "browser",  # Camera is managed by browser getUserMedia
        "model": model_status,
        "arduino": arduino_status,
        "servo": servo_status,
        "serial_port": SERIAL_PORT,
        "current_servo_angle": serial_service.current_servo_angle,
        "available_ports": serial_service.list_ports(),
    }


@app.get("/system-info", response_model=SystemInfoResponse)
async def get_system_info():
    """
    Get CPU, Memory, and GPU usage for the sidebar display.
    Uses psutil for real system metrics if available.
    """
    cpu = 0.0
    mem = 0.0
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
    except ImportError:
        pass

    # GPU detection — try to get from TensorFlow
    gpu_percent = None
    gpu_available = False
    try:
        import tensorflow as tf
        gpus = tf.config.list_physical_devices("GPU")
        gpu_available = len(gpus) > 0
    except Exception:
        pass
        # Note: Real-time GPU utilization % requires nvidia-smi or pynvml.
        # We report availability but not utilization to avoid fake values.
    except Exception:
        pass

    return {
        "cpu_percent": cpu,
        "memory_percent": mem,
        "gpu_percent": gpu_percent,
        "gpu_available": gpu_available,
    }


# ---- Serial / Arduino Endpoints ----

@app.post("/serial/connect")
async def serial_connect(port: str | None = None):
    """Connect to Arduino on specified port (defaults to config)."""
    success = serial_service.connect(port)
    return {
        "success": success,
        "status": serial_service.status,
        "port": port or SERIAL_PORT,
    }


@app.post("/serial/disconnect")
async def serial_disconnect():
    """Disconnect from Arduino."""
    serial_service.disconnect()
    return {"success": True, "status": "disconnected"}


@app.get("/serial/ports")
async def serial_ports():
    """List all available serial/COM ports."""
    return {"ports": serial_service.list_ports()}


@app.post("/serial/test")
@app.post("/hardware/servo/test")
async def servo_test(payload: dict | None = None, angle: int | None = None):
    """
    Send a test angle to Arduino to execute the full sorting cycle:
      0° ➔ target_angle ➔ 0° (home return)

    Accepts body `{"angle": 30}` or query param `?angle=30`.
    """
    target = angle
    if payload and "angle" in payload:
        target = payload["angle"]

    if target is None:
        target = 90

    if not (0 <= target <= 180):
        raise HTTPException(status_code=400, detail="Angle must be between 0 and 180 degrees.")

    result = serial_service.send_angle(target)
    return result


@app.get("/hardware/status")
async def get_hardware_status():
    """Get structured hardware status for Arduino and Servo."""
    return serial_service.get_hardware_status()


# ---- Health Check ----

@app.get("/")
async def root():
    """Health check — confirms the API is running."""
    return {
        "name": "Smart Fruit Sorting System",
        "status": "running",
        "model_status": get_model_status(),
        "arduino_status": serial_service.status,
    }
