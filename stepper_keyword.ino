#include <AccelStepper.h>
#include <Arduino_RouterBridge.h>

// Define CNC Shield pins for X-axis
#define X_STEP_PIN 2
#define X_DIR_PIN 5
#define ENABLE_PIN 8

// Create an AccelStepper object in DRIVER mode (step + direction)
AccelStepper stepperX(AccelStepper::DRIVER, X_STEP_PIN, X_DIR_PIN);

// Motion control flags
bool isMoving = false;
bool returning = false;

void setup() {
  pinMode(ENABLE_PIN, OUTPUT);
  digitalWrite(ENABLE_PIN, LOW); // enable driver
  Bridge.begin();
  Bridge.provide("keyword_detected", startMove);

  stepperX.setMaxSpeed(1000);
  stepperX.setAcceleration(200);
}

void loop() {
  if (isMoving) {
    stepperX.run();

    // When we reach the target
    if (stepperX.distanceToGo() == 0) {
      if (!returning) {
        // Finished forward move — now go back
        returning = true;
        delay(500); // small pause at the end
        stepperX.moveTo(0);
      } else {
        // Finished returning — done!
        isMoving = false;
        returning = false;
        digitalWrite(ENABLE_PIN, HIGH); // optional: disable driver to save power
      }
    }
  }
}

// Called when keyword is detected
void startMove() {
  // Only trigger if not already moving
  if (!isMoving) {
    digitalWrite(ENABLE_PIN, LOW); // ensure driver is enabled
    stepperX.moveTo(1000);
    isMoving = true;
    returning = false;
  }
}
