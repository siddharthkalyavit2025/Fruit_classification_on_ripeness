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
        self._last_command_prediction_id: int | None = None  # duplicate guard

    @property
    def status(self) -> str:
        """Current connection status: 'connected', 'disconnected', 'error'."""
        return self._status

    @property
    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

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
            port: COM port (e.g., "COM3"). Uses config default if None.

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
                # Arduino UNO resets when serial opens — need ~2s
                time.sleep(2)

                # Read the startup message ("EcoVision Servo Ready")
                if self._serial.in_waiting > 0:
                    startup_msg = self._serial.readline().decode("utf-8", errors="ignore").strip()
                    logger.info(f"Arduino says: {startup_msg}")

                self._status = "connected"
                logger.info(f"✅ Connected to Arduino on {port}")
                return True

            except serial.SerialException as e:
                logger.error(f"❌ Failed to connect to {port}: {e}")
                self._status = "error"
                self._serial = None
                return False

    def disconnect(self):
        """Close the serial connection."""
        with self._lock:
            if self._serial and self._serial.is_open:
                try:
                    self._serial.close()
                    logger.info("Disconnected from Arduino")
                except Exception as e:
                    logger.error(f"Error disconnecting: {e}")
            self._serial = None
            self._status = "disconnected"

    def send_angle(self, angle: int, prediction_id: int | None = None) -> dict:
        """
        Send a servo angle command to Arduino.

        Args:
            angle: Target servo angle (0-180)
            prediction_id: Optional — prevents duplicate commands for same prediction

        Returns:
            {
                "success": True/False,
                "response": "OK: moved to 120 degrees",
                "angle_sent": 120
            }
        """
        # Duplicate guard
        if prediction_id is not None and prediction_id == self._last_command_prediction_id:
            logger.warning(f"Duplicate command blocked for prediction #{prediction_id}")
            return {
                "success": False,
                "error": "Duplicate command — already sent for this prediction",
                "angle_sent": angle,
            }

        if not SERIAL_ENABLED:
            logger.info(f"[SERIAL DISABLED] Would send angle: {angle}")
            if prediction_id:
                self._last_command_prediction_id = prediction_id
            return {
                "success": True,
                "response": f"[SERIAL DISABLED] Simulated: angle {angle}",
                "angle_sent": angle,
            }

        with self._lock:
            if not self.is_connected:
                return {
                    "success": False,
                    "error": "Arduino not connected",
                    "angle_sent": angle,
                }

            try:
                # Validate angle range
                if not (0 <= angle <= 180):
                    return {
                        "success": False,
                        "error": f"Invalid angle: {angle}. Must be 0-180.",
                        "angle_sent": angle,
                    }

                # Send the angle as ASCII string with newline
                # This matches the Arduino code: Serial.readStringUntil('\n')
                command = f"{angle}\n"
                self._serial.write(command.encode("utf-8"))
                logger.info(f"Sent to Arduino: {angle}")

                # Read response from Arduino
                raw_bytes = self._serial.readline()
                response = raw_bytes.decode("utf-8", errors="ignore").strip()
                logger.info(f"Arduino response: {response} (raw bytes: {raw_bytes!r})")
                success = (
                    response.startswith("OK:")
                    or response.startswith("SERVO_MOVED:")
                    or response.startswith("DONE")
                    or (len(response) > 0 and not response.startswith("ERR:"))
                )
                logger.info(f"Parsed success={success} for response={response!r}")

                # Update duplicate guard
                if prediction_id:
                    self._last_command_prediction_id = prediction_id

                return {
                    "success": success,
                    "response": response,
                    "angle_sent": angle,
                }

            except serial.SerialException as e:
                logger.error(f"Serial communication error: {e}")
                self._status = "error"
                return {
                    "success": False,
                    "error": str(e),
                    "angle_sent": angle,
                }


# ---- Singleton Instance ----
serial_service = SerialService()
