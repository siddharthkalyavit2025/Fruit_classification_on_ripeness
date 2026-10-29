/* ====================================================================
   Fruit Sorting System — Arduino Servo Control Sketch
   ====================================================================
   Receives target angle commands over Serial from FastAPI Backend.
   Executes the sorting cycle:
     Home/Center (90°) → 0.5s Delay → Target Angle → Return Home (90°)
     Unripe (90°) : Motor does NOT move — stays at center.
     Ripe   (30°) : 60° to the LEFT  — returns immediately to 90°.
     Rotten (150°): 60° to the RIGHT — returns immediately to 90°.

   Protocol:
     - Baud Rate: 9600
     - Input Command: "{angle}\n" (e.g., "30\n", "90\n", "150\n")
     - Output Step 1: "SERVO_MOVED:{angle}\n"
     - Output Step 2: "SERVO_HOME:90\n"
   ==================================================================== */

#include <Servo.h>

Servo sortingServo;
const int SERVO_PIN = 9;
const int HOME_ANGLE = 90;          // Official Center / Home Position
const int INITIAL_DELAY_MS = 500;   // 0.5s delay before moving motor
const int SORTING_HOLD_MS = 700;    // 0.7s hold at target angle so servo completes rotation

void setup() {
  Serial.begin(9600);
  sortingServo.attach(SERVO_PIN);

  // Initialize to Home Position (90°)
  sortingServo.write(HOME_ANGLE);
  delay(500);

  // Ready signal to FastAPI Backend
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
        if (targetAngle == HOME_ANGLE) {
          // Unripe: Do not move motor, stay at home center (90°)
          Serial.print("SERVO_MOVED:");
          Serial.println(HOME_ANGLE);
          Serial.print("SERVO_HOME:");
          Serial.println(HOME_ANGLE);
        } else {
          // Step 1: 0.5s delay before moving motor
          delay(INITIAL_DELAY_MS);

          // Step 2: Move to target angle
          // Ripe   → 30°  (60° left  from center)
          // Rotten → 150° (60° right from center)
          sortingServo.write(targetAngle);

          Serial.print("SERVO_MOVED:");
          Serial.println(targetAngle);

          // Step 3: Hold at target angle so servo physically completes rotation
          delay(SORTING_HOLD_MS);

          // Step 4: Return to Home position (90°)
          sortingServo.write(HOME_ANGLE);

          // Step 5: Completion acknowledgement to backend
          Serial.print("SERVO_HOME:");
          Serial.println(HOME_ANGLE);
        }
      } else {
        Serial.print("ERR: Invalid angle ");
        Serial.println(inputString);
      }
    }
  }
}
