# 🍎 Smart Fruit Sorting System — AI-Powered Fruit Ripeness & Quality Classification

An end-to-end **AI-powered fruit classification and automated hardware sorting system**. 
Using **Deep Learning (EfficientNetV2-S)** and real-time computer vision, this project identifies fruit types (Apple, Banana, Orange) and their condition (Fresh/Ripe, Unripe, Rotten) across **9 distinct classes**. The system directly communicates with an **Arduino UNO** over USB Serial to actuate a servo motor, directing physical fruits into designated sorting bins.

---

## 🌟 Key Features

- **🧠 Deep Learning Engine**: Powered by `EfficientNetV2-S` fine-tuned on fruit ripeness datasets across 9 classes (Fresh/Unripe/Rotten for Apple, Banana, and Orange).
- **📸 Multi-Camera & iVCam Auto-Detection**: Live webcam stream supporting device switching, auto-detection for iVCam (phone as webcam), frame capture, and image upload.
- **⚡ Non-Blocking Background Sorting**: Uses FastAPI `BackgroundTasks` so AI inference, class confidence scores, and metrics render immediately on the UI without waiting for servo actuation.
- **🤖 Automated Servo Motor Sorting**: Direct USB Serial communication (`COM6` / `9600` Baud) with Arduino UNO actuating a 3-way servo mechanism (Center 90°, Left 30°, Right 150°).
- **🎨 Glassmorphic Responsive Dashboard**: Modern dark-mode UI built with React & Vite, featuring live video streams, angle gauges, fruit icons, and hardware connection toggles.
- **📊 Real-Time Analytics & Stats**: SQLite-backed predictions tracking total counts, high-confidence ratios, sorting success rates, and distribution per fruit.
- **🔄 Live Serial Reconnection & Diagnostics**: Header connection badge with one-click connect/disconnect, automatic COM port scanning, hardware health checks, and manual angle testing.

---

## 📐 Ripeness Classification & Servo Sorting Protocol

The AI model classifies images into **9 distinct categories**:
- **Apples**: `freshapples`, `unripe apple`, `rottenapples`
- **Bananas**: `freshbanana`, `unripe banana`, `rottenbanana`
- **Oranges**: `freshoranges`, `unripe orange`, `rottenoranges`

Physical sorting is routed into 3 primary destinations based on the fruit's **ripeness condition**:

| Condition | Bin Destination | Emoji | Servo Position | Target Angle | Hardware Sorting Cycle |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Fresh / Ripe** | **Ripe Bin** | 🍎🍌🍊 | 60° Left of Center | **30°** | 0.5s delay ➔ Rotate to 30° ➔ 0.7s hold for fruit drop ➔ Return to 90° Home |
| **Unripe** | **Unripe Bin** | 🍏🍌🍊 | Center / Neutral | **90°** | Motor stays stationary at 90° Home (no actuation needed) |
| **Rotten** | **Reject Bin** | 🥀 | 60° Right of Center | **150°** | 0.5s delay ➔ Rotate to 150° ➔ 0.7s hold for fruit drop ➔ Return to 90° Home |

> **Note**: Angles and timing parameters can be adjusted in [`backend/config.py`](backend/config.py) (`SORTING_MAP`, `SERVO_HOME_ANGLE`) and [`arduino/fruit_sorter.ino`](arduino/fruit_sorter.ino).

---

## 🛠 Tech Stack & Architecture

### **Frontend**
- **Framework**: React 18 + Vite
- **Styling**: Vanilla CSS (CSS Grid, Glassmorphic Glass Design, Custom Color System)
- **Camera Handling**: MediaDevices API with dynamic camera enumeration and iVCam auto-selection
- **Icons & Visualization**: Lucide React Icons, Custom SVG Fruit Assets

### **Backend**
- **Framework**: FastAPI (Python 3.10+) with non-blocking `BackgroundTasks`
- **ML Framework**: TensorFlow 2.16+ / Keras
- **Model**: EfficientNetV2-S (weights included in repository)
- **Database**: SQLite (`predictions.db`)
- **System Monitoring**: `psutil` (CPU and RAM telemetry)
- **Hardware Integration**: `pyserial` for bidirectional USB Serial Communication

### **Hardware**
- **Microcontroller**: Arduino UNO
- **Actuator**: SG90 / MG996R Servo Motor (PWM Pin 9)
- **Interface**: USB Serial (`COM6` / `9600` Baud)
- **Default Position**: 90° (Neutral / Home)

---

## 📁 Repository Structure

```
Fruit_classification_on_ripeness/
├── arduino/
│   └── fruit_sorter.ino          # Arduino C++ sketch for servo motor actuation (90° Home)
├── backend/
│   ├── database/                 # SQLite database connection & schema initialization
│   ├── hardware/                 # Serial communication service & sorting angle manager
│   ├── model/
│   │   ├── weights/              # Pre-trained EfficientNetV2-S weights (.h5)
│   │   ├── class_mapping.py      # 9-class human-readable mapping
│   │   ├── model_loader.py       # Keras model builder & weight loader
│   │   └── predictor.py          # Image preprocessing & inference pipeline
│   ├── schemas/                  # Pydantic request/response models
│   ├── services/                 # Prediction orchestration & DB persistence
│   ├── config.py                 # Centralized configuration (ports, angles, thresholds)
│   ├── main.py                   # FastAPI REST API application
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── public/                   # Static fruit icons (apple, banana, orange logos)
│   ├── src/
│   │   ├── components/           # LiveCamera, AIPrediction, SortingAction, SystemStatus, Statistics, Header, Sidebar
│   │   ├── services/             # Axios API service layer
│   │   ├── App.jsx               # Main React dashboard layout
│   │   └── index.css             # Design tokens & dark mode styling
│   ├── package.json              # Node dependencies
│   └── vite.config.js            # Vite configuration
└── README.md                     # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python**: `3.10` or higher
- **Node.js**: `18.x` or higher
- **Arduino IDE**: Version 1.8+ or 2.x (for flashing Arduino UNO)

---

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
python main.py
```
The FastAPI backend server will start at `http://localhost:8000`. You can inspect interactive Swagger docs at `http://localhost:8000/docs`.

---

### 3. Frontend Setup

```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install Node modules
npm install

# Start Vite development server
npm run dev -- --port 3000
```
Open your browser and navigate to `http://localhost:3000`.

---

### 4. Hardware Setup (Arduino UNO)

1. Connect your **Arduino UNO** to your computer via USB (default port: `COM6`).
2. Attach the **Servo Motor**:
   - **Signal Line (Yellow/Orange)** ➔ Arduino **Digital Pin 9**
   - **VCC (Red)** ➔ Arduino **5V**
   - **GND (Black/Brown)** ➔ Arduino **GND**
3. Open `arduino/fruit_sorter.ino` in the Arduino IDE.
4. Select board **Arduino Uno** and your COM port (`COM6`).
5. Click **Upload**.
6. When power is applied, the servo will automatically align to **90° (Home)** and transmit `ARDUINO_READY`.

---

## 🔌 API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Health check & system component readiness probe |
| `POST` | `/predict` | Upload image file (`multipart/form-data`) for AI inference, DB record, and background servo actuation |
| `GET` | `/predictions?limit=20` | Fetch recent prediction history |
| `DELETE` | `/predictions/{id}` | Delete a prediction record from database |
| `GET` | `/stats` | Retrieve overall fruit counts, accuracy ratios, and condition distribution |
| `GET` | `/status` | System health, model readiness, and serial port details |
| `GET` | `/system-info` | Real-time CPU, RAM, and GPU telemetry for the dashboard |
| `GET` | `/hardware/status` | Structured Arduino connection and servo position status |
| `GET` | `/serial/ports` | List all available COM ports on the system |
| `POST` | `/serial/connect?port=COM6` | Connect or switch Arduino USB serial port |
| `POST` | `/serial/disconnect` | Safely disconnect Arduino serial communication |
| `POST` | `/serial/test?angle=90` | Send test angle to verify servo movement and home return cycle |

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
