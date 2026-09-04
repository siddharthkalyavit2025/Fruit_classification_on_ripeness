# ==============================================================
# Smart Fruit Sorting System — Centralized Configuration
# ==============================================================
# All configurable values live here. Change servo angles,
# serial port, camera index, etc. in ONE place.
# ==============================================================

import os

# ----------------------------------------------------------
# Paths
# ----------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRIMARY_WEIGHTS_PATH = os.path.join(BASE_DIR, "model", "weights", "fruit_efficientnetv2s.weights.h5")
FALLBACK_WEIGHTS_PATH = os.path.join(BASE_DIR, "..", "fruit_efficientnetv2s.weights.h5")
MODEL_WEIGHTS_PATH = PRIMARY_WEIGHTS_PATH if os.path.exists(PRIMARY_WEIGHTS_PATH) else FALLBACK_WEIGHTS_PATH
DATABASE_PATH = os.path.join(BASE_DIR, "predictions.db")

# ----------------------------------------------------------
# Model
# ----------------------------------------------------------
MODEL_INPUT_SIZE = (224, 224)
NUM_CLASSES = 9

# The 9 classes in the EXACT order the model was trained on.
# ImageDataGenerator.flow_from_directory() sorts alphabetically.
CLASS_NAMES = [
    "freshapples",      # 0
    "freshbanana",      # 1
    "freshoranges",     # 2
    "rottenapples",     # 3
    "rottenbanana",     # 4
    "rottenoranges",    # 5
    "unripe apple",     # 6
    "unripe banana",    # 7
    "unripe orange",    # 8
]

# ----------------------------------------------------------
# Class → Human-readable mapping
# ----------------------------------------------------------
# Each entry: { fruit, condition, emoji }
CLASS_INFO = {
    "freshapples":   {"fruit": "Apple",  "condition": "Fresh/Ripe", "emoji": "🍎"},
    "freshbanana":   {"fruit": "Banana", "condition": "Fresh/Ripe", "emoji": "🍌"},
    "freshoranges":  {"fruit": "Orange", "condition": "Fresh/Ripe", "emoji": "🍊"},
    "rottenapples":  {"fruit": "Apple",  "condition": "Rotten",     "emoji": "🍎"},
    "rottenbanana":  {"fruit": "Banana", "condition": "Rotten",     "emoji": "🍌"},
    "rottenoranges": {"fruit": "Orange", "condition": "Rotten",     "emoji": "🍊"},
    "unripe apple":  {"fruit": "Apple",  "condition": "Unripe",     "emoji": "🍏"},
    "unripe banana": {"fruit": "Banana", "condition": "Unripe",     "emoji": "🍌"},
    "unripe orange": {"fruit": "Orange", "condition": "Unripe",     "emoji": "🍊"},
}

# ----------------------------------------------------------
# Sorting Map — condition → destination + servo angle
# ----------------------------------------------------------
# Servo angles are CONFIGURABLE. Change them here after
# assembling the physical sorting mechanism.
# ----------------------------------------------------------
SORTING_MAP = {
    "Fresh/Ripe": {
        "destination": "Ripe Bin",
        "servo_angle": 120,
    },
    "Rotten": {
        "destination": "Reject Bin",
        "servo_angle": 60,
    },
    "Unripe": {
        "destination": "Unripe Bin",
        "servo_angle": 30,
    },
}

# ----------------------------------------------------------
# Arduino Serial Communication
# ----------------------------------------------------------
SERIAL_PORT = os.environ.get("SERIAL_PORT", "COM6")
SERIAL_BAUD_RATE = 9600
SERIAL_TIMEOUT = 2          # seconds to wait for Arduino response
SERIAL_ENABLED = True       # set False to run without Arduino

# ----------------------------------------------------------
# Camera
# ----------------------------------------------------------
CAMERA_INDEX = int(os.environ.get("CAMERA_INDEX", "0"))

# ----------------------------------------------------------
# FastAPI
# ----------------------------------------------------------
API_HOST = "0.0.0.0"
API_PORT = 8000
CORS_ORIGINS = [
    "http://localhost:5173",    # Vite dev server
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
