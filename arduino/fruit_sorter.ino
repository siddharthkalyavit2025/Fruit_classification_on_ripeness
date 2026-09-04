/* ====================================================================
   Fruit Sorting System — Arduino Servo Control Sketch
   ====================================================================
   Receives target angle commands over Serial from the FastAPI Backend
   and moves the sorting servo motor to direct fruits to sorting bins.

   Protocol:
     - Serial Baud Rate: 9600
     - Input Command: "{angle}\n" (e.g. "90\n", "120\n", "180\n")
     - Output Response: "SERVO_MOVED:{angle}\n"
   ==================================================================== */

#include <Servo.h>

Servo sortingServo;
const int SERVO_PIN = 9;
const int INITIAL_ANGLE = 90;

void setup() {
  Serial.begin(9600);
  sortingServo.attach(SERVO_PIN);
  sortingServo.write(INITIAL_ANGLE);
  
  // Wait for serial buffer stabilization
  delay(500);
  Serial.println("ARDUINO_READY");
}

void loop() {
  if (Serial.available() > 0) {
    String inputString = Serial.readStringUntil('\n');
    inputString.trim();

    if (inputString.length() > 0) {
      int targetAngle = inputString.toInt();

      // Validate angle range (0° - 180°)
      if (targetAngle >= 0 && targetAngle <= 180) {
        sortingServo.write(targetAngle);
        delay(300); // Allow servo movement time
        
        Serial.print("SERVO_MOVED:");
        Serial.println(targetAngle);
      } else {
        Serial.print("ERR: Invalid angle ");
        Serial.println(inputString);
      }
    }
  }
}
