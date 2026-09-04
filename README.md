# 🍎 Smart Fruit Sorting System — AI-Powered Fruit Ripeness & Quality Classification

An end-to-end **AI-powered fruit classification and automated hardware sorting system**. 
Using **Deep Learning (EfficientNetV2-S)** and real-time computer vision, this project identifies fruit types (Apple, Banana, Orange) and their condition (Fresh/Ripe, Unripe, Rotten) across **9 distinct classes**. The system directly communicates with an **Arduino UNO** over USB Serial to actuate a servo motor, directing physical fruits into designated sorting bins.

---

## 🌟 Key Features

- **🧠 Deep Learning Engine**: Powered by `EfficientNetV2-S` fine-tuned on fruit ripeness datasets.
- **📸 Real-Time Computer Vision Feed**: Live webcam stream with one-click frame capture and image file upload options.
- **🤖 Automated Servo Motor Sorting**: Direct USB Serial communication (COM port) actuating an Arduino-driven servo motor (0° to 180°) based on classification results.
- **🎨 Glassmorphic Responsive Dashboard**: Built with React & Vite, styled in modern dark mode featuring fruit logos, live status indicators, angle gauges, and metrics.
- **📊 Real-Time Analytics & Stats**: SQLite-backed predictions database tracking overall detection counts, high-confidence ratios, sorting success rates, and distribution per fruit.
- **🔄 Live Serial Reconnection**: Header connection badge allows instant connection/disconnection toggling with auto-port detection (`COM6`).

---

## 📐 Servo Angles & Ripeness Classification Protocol

| Fruit Class | Condition | Emoji | Bin Destination | Target Servo Angle |
| :--- | :--- | :---: | :--- | :---: |
| **`freshapples`** | Fresh / Ripe | 🍎 | Fresh Apple Bin | **30°** |
| **`unripe apple`** | Unripe | 🍏 | Unripe Apple Bin | **45°** |
| **`rottenapples`** | Rotten | 🍎 | Rotten Apple Bin | **60°** |
| **`freshbanana`** | Fresh / Ripe | 🍌 | Fresh Banana Bin | **90°** |
| **`unripe banana`** | Unripe | 🍌 | Unripe Banana Bin | **105°** |
| **`rottenbanana`** | Rotten | 🍌 | Rotten Banana Bin | **120°** |
| **`freshoranges`** | Fresh / Ripe | 🍊 | Fresh Orange Bin | **150°** |
| **`unripe orange`** | Unripe | 🍊 | Unripe Orange Bin | **165°** |
| **`rottenoranges`** | Rotten | 🍊 | Rotten Orange Bin | **180°** |

---

## 🛠 Tech Stack & Architecture

### **Frontend**
- **Framework**: React 18 + Vite
- **Styling**: Vanilla CSS (CSS Grid, Glassmorphic Glass Design, Custom Color System)
- **Icons & Visualization**: Lucide React Icons, Custom SVG Fruit Assets

### **Backend**
- **Framework**: FastAPI (Python 3.10)
- **ML Framework**: TensorFlow 2.16+ / Keras
- **Model**: EfficientNetV2-S (weights included in repository)
- **Database**: SQLite (`predictions.db`)
- **Hardware Integration**: `pyserial` for USB Serial Communication

### **Hardware**
- **Microcontroller**: Arduino UNO
- **Actuator**: SG90 / MG996R Servo Motor (PWM Pin 9)
- **Interface**: USB Serial (`COM6` / `9600` Baud)

---

## 📁 Repository Structure

```
Fruit_classification_on_ripeness/
├── arduino/
│   └── fruit_sorter.ino          # Arduino C++ sketch for servo motor actuation
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
3. Open `arduino/fruit_sorter.ino` in Arduino IDE.
4. Select board **Arduino Uno** and your COM port (`COM6`).
5. Click **Upload**.

---

## 🔌 API Endpoints Summary

- `GET /status` — System health, model readiness, and serial port details.
- `POST /predict/file` — Upload image file for inference, database logging, and automated servo actuation.
- `POST /predict/base64` — Send base64 image frame from webcam feed for inference.
- `POST /serial/connect?port=COM6` — Connect or switch Arduino USB serial port.
- `POST /serial/disconnect` — Safely disconnect Arduino serial communication.
- `POST /serial/test?angle=90` — Manually test servo motor angle.
- `GET /stats` — Retrieve overall fruit counts, accuracy statistics, and distribution.
- `GET /predictions` — Fetch recent prediction history.
- `DELETE /predictions/{id}` — Delete a prediction record.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
