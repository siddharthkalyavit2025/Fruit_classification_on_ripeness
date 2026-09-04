/* ====================================================================
   Fruit Sorting System — Arduino Servo Control Sketch
   ====================================================================
   Receives target angle commands over Serial from FastAPI Backend.
   Executes the full sorting cycle:
     Home (0°) ➔ Target Angle ➔ Sorting Wait ➔ Return Home (0°)

   Protocol:
     - Baud Rate: 9600
     - Input Command: "{angle}\n" (e.g., "30\n", "120\n")
     - Output Step 1: "SERVO_MOVED:{angle}\n"
     - Output Step 2: "SERVO_HOME:0\n"
   ==================================================================== */

#include <Servo.h>

Servo sortingServo;
const int SERVO_PIN = 9;
const int HOME_ANGLE = 0;       // Official Home/Idle Position
const int SORTING_WAIT_MS = 1200; // Duration fruit takes to fall into bin

void setup() {
  Serial.begin(9600);
  sortingServo.attach(SERVO_PIN);
  
  // Initialize to Home Position (0°)
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
        // Step 1: Move to target angle
        sortingServo.write(targetAngle);
        delay(400); // Servo actuation time
        
        Serial.print("SERVO_MOVED:");
        Serial.println(targetAngle);

        // Step 2: Wait while fruit drops into sorting bin
        delay(SORTING_WAIT_MS);

        // Step 3: Return to Home position (0°)
        sortingServo.write(HOME_ANGLE);
        delay(400); // Return travel time

        // Step 4: Completion acknowledgement to backend
        Serial.println("SERVO_HOME:0");
      } else {
        Serial.print("ERR: Invalid angle ");
        Serial.println(inputString);
      }
    }
  }
}
