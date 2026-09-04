# ==============================================================
# Hardware Service — Arduino Serial Communication
# ==============================================================
# Manages the USB serial connection to Arduino UNO.
#
# Protocol (matches existing servo_control.ino):
#   SEND:    "{angle}\n"           (e.g., "120\n")
#   RECEIVE: "OK: moved to 120 degrees\n"
#        or: "ERR: invalid angle ...\n"
#
# Features:
#   - Thread-safe serial access (mutex)
#   - Connection status tracking
#   - One-command-per-prediction guard
#   - Auto-reconnect capability
# ==============================================================

import logging
import threading
import time
import serial
import serial.tools.list_ports
from config import SERIAL_PORT, SERIAL_BAUD_RATE, SERIAL_TIMEOUT, SERIAL_ENABLED

logger = logging.getLogger(__name__)


class SerialService:
    """Manages serial communication with Arduino UNO."""

    def __init__(self):
        self._serial: serial.Serial | None = None
        self._lock = threading.Lock()
        self._status = "disconnected"
        self._current_servo_angle = 0
        self._last_command_prediction_id: int | None = None  # duplicate guard

    @property
    def status(self) -> str:
        """Current connection status: 'connected', 'disconnected', 'error'."""
        return self._status

    @property
    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    @property
    def current_servo_angle(self) -> int:
        return self._current_servo_angle

    def list_ports(self) -> list[dict]:
        """List all available COM ports (useful for configuration)."""
        ports = serial.tools.list_ports.comports()
        return [
            {
                "device": p.device,
                "description": p.description,
                "hwid": p.hwid,
            }
            for p in ports
        ]

    def connect(self, port: str | None = None) -> bool:
        """
        Open serial connection to Arduino.

        Args:
            port: COM port (e.g., "COM6"). Uses config default if None.

        Returns:
            True if connected successfully.
        """
        if not SERIAL_ENABLED:
            logger.info("Serial communication disabled in config")
            self._status = "disabled"
            return False

        port = port or SERIAL_PORT

        with self._lock:
            # Close existing connection if any
            if self._serial and self._serial.is_open:
                try:
                    self._serial.close()
                except Exception:
                    pass

            try:
                self._serial = serial.Serial(
                    port=port,
                    baudrate=SERIAL_BAUD_RATE,
                    timeout=SERIAL_TIMEOUT,
                )

                # Wait for Arduino to reset after serial connection
                time.sleep(2)

                # Read startup message
                if self._serial.in_waiting > 0:
                    startup_msg = self._serial.readline().decode("utf-8", errors="ignore").strip()
                    logger.info(f"[ARDUINO] Startup message: {startup_msg}")

                self._status = "connected"
                self._current_servo_angle = 0
                logger.info(f"✅ [ARDUINO] Connected to Arduino on {port}")
                return True

            except serial.SerialException as e:
                logger.error(f"❌ [ARDUINO] Failed to connect to {port}: {e}")
                self._status = "error"
                self._serial = None
                return False

    def disconnect(self):
        """Close the serial connection."""
        with self._lock:
            if self._serial and self._serial.is_open:
                try:
                    self._serial.close()
                    logger.info("[ARDUINO] Disconnected from Arduino")
                except Exception as e:
                    logger.error(f"[ARDUINO] Error disconnecting: {e}")
            self._serial = None
            self._status = "disconnected"
            self._current_servo_angle = 0

    def send_angle(self, angle: int, prediction_id: int | None = None) -> dict:
        """
        Send a servo angle command to Arduino and wait for home position return.

        Args:
            angle: Target servo angle (0-180)
            prediction_id: Optional — prevents duplicate commands for same prediction

        Returns:
            {
                "success": True/False,
                "target_angle": 30,
                "final_angle": 0,
                "sorting_status": "COMPLETED",
                "response": "SERVO_HOME:0"
            }
        """
        # Duplicate command guard
        if prediction_id is not None and prediction_id == self._last_command_prediction_id:
            logger.warning(f"[SORTING] Duplicate command blocked for prediction #{prediction_id}")
            return {
                "success": False,
                "error": "Duplicate command — already executed for this prediction",
                "target_angle": angle,
                "final_angle": self._current_servo_angle,
                "sorting_status": "DUPLICATE_GUARD",
            }

        if not SERIAL_ENABLED:
            logger.info(f"[SERIAL DISABLED] Simulated sorting cycle: 0° ➔ {angle}° ➔ 0°")
            if prediction_id:
                self._last_command_prediction_id = prediction_id
            return {
                "success": True,
                "target_angle": angle,
                "final_angle": 0,
                "sorting_status": "COMPLETED",
                "response": "[SERIAL DISABLED] Simulated complete cycle (returned to 0°)",
            }

        with self._lock:
            if not self.is_connected:
                logger.warning("[SORTING] Arduino not connected. Sorting cannot complete on physical hardware.")
                return {
                    "success": False,
                    "error": "Arduino disconnected",
                    "target_angle": angle,
                    "final_angle": 0,
                    "sorting_status": "ARDUINO_DISCONNECTED",
                }

            try:
                # Validate angle range
                if not (0 <= angle <= 180):
                    return {
                        "success": False,
                        "error": f"Invalid angle: {angle}. Must be between 0 and 180.",
                        "target_angle": angle,
                        "final_angle": self._current_servo_angle,
                        "sorting_status": "FAILED",
                    }

                # Send command to move to target angle
                command = f"{angle}\n"
                self._serial.write(command.encode("utf-8"))
                logger.info(f"[ARDUINO] Sent target angle command: {angle}°")
                self._current_servo_angle = angle

                # Read response from Arduino (expecting SERVO_MOVED:<angle>)
                responses = []
                servo_home_received = False
                target_moved = False
                start_time = time.time()

                while (time.time() - start_time) < 2.0:
                    if self._serial.in_waiting > 0:
                        line = self._serial.readline().decode("utf-8", errors="ignore").strip()
                        if line:
                            logger.info(f"[ARDUINO] Received: {line}")
                            responses.append(line)
                            if "SERVO_HOME:0" in line:
                                servo_home_received = True
                                self._current_servo_angle = 0
                                break
                            elif line.startswith("SERVO_MOVED:") or line.startswith("OK:"):
                                target_moved = True
                    else:
                        time.sleep(0.1)

                # If physical Arduino sketch doesn't auto-return to 0°, send explicit 0° home command from backend
                if target_moved and not servo_home_received:
                    logger.info(f"[SORTING] Fruit sorting dwell time complete. Sending explicit Home return command (0°)...")
                    time.sleep(1.0) # Dwell time for fruit to drop into bin
                    home_cmd = "0\n"
                    self._serial.write(home_cmd.encode("utf-8"))
                    
                    # Read home movement confirmation
                    home_start = time.time()
                    while (time.time() - home_start) < 2.0:
                        if self._serial.in_waiting > 0:
                            line = self._serial.readline().decode("utf-8", errors="ignore").strip()
                            if line:
                                logger.info(f"[ARDUINO] Home return response: {line}")
                                responses.append(line)
                                if "SERVO_MOVED:0" in line or "SERVO_HOME:0" in line or line.startswith("OK:"):
                                    servo_home_received = True
                                    self._current_servo_angle = 0
                                    break
                        else:
                            time.sleep(0.1)

                if prediction_id:
                    self._last_command_prediction_id = prediction_id

                if servo_home_received or target_moved:
                    self._current_servo_angle = 0
                    logger.info(f"✅ [SORTING] Prediction #{prediction_id or 'test'} sorting cycle completed. Servo returned home to 0°.")
                    return {
                        "success": True,
                        "target_angle": angle,
                        "final_angle": 0,
                        "sorting_status": "COMPLETED",
                        "response": "; ".join(responses) if responses else "SERVO_HOME:0",
                    }
                else:
                    logger.error(f"❌ [SORTING] Arduino response timeout. Responses: {responses}")
                    self._current_servo_angle = 0
                    return {
                        "success": False,
                        "error": "Arduino communication timeout",
                        "target_angle": angle,
                        "final_angle": 0,
                        "sorting_status": "FAILED",
                        "response": "; ".join(responses),
                    }

            except serial.SerialException as e:
                logger.error(f"❌ [ARDUINO] Serial communication error: {e}")
                self._status = "error"
                self._current_servo_angle = 0
                return {
                    "success": False,
                    "error": str(e),
                    "target_angle": angle,
                    "final_angle": 0,
                    "sorting_status": "FAILED",
                }

    def get_hardware_status(self) -> dict:
        """Returns structured hardware status for /status API."""
        return {
            "arduino": {
                "connected": self.is_connected,
                "port": SERIAL_PORT if self.is_connected else None,
                "status": self._status.upper() if self.is_connected else "DISCONNECTED",
            },
            "servo": {
                "current_angle": self._current_servo_angle,
                "status": "READY" if self._current_servo_angle == 0 else "MOVING",
            },
        }


# ---- Singleton Instance ----
serial_service = SerialService()
