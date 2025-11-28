#include <Arduino_RouterBridge.h>
#include <AccelStepper.h>
#include <Servo.h>

#define STEP_PIN 2
#define DIR_PIN 5
#define ENABLE_PIN 8
#define LIMIT_PIN 9
#define SERVO_PIN 11

AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);
Servo myservo;

bool homed = false;
long positions[6] = {0, 33, 66, 99, 132, 165};

void servoDrop() {
    myservo.write(35);
    delay(2000);
    myservo.write(75);
    delay(500);
}

void movePos(int n) {
    if (n < 1 || n > 6) return;
    delay(2000);

    long target = positions[n - 1];
    Monitor.println("moving stepper");
    stepper.moveTo(target);

    while (stepper.distanceToGo() != 0)
        stepper.run();

    servoDrop();

    int var = 0;
    Monitor.println("sending ack");

    stepper.moveTo(10);
    while (stepper.distanceToGo() != 0)
        stepper.run();

    Bridge.notify("ack", var);
}

void setup() {
    pinMode(ENABLE_PIN, OUTPUT);
    digitalWrite(ENABLE_PIN, LOW);
    pinMode(LIMIT_PIN, INPUT_PULLUP);

    Bridge.begin();
    Monitor.begin(115200);

    myservo.attach(SERVO_PIN);

    stepper.setMaxSpeed(1000);
    stepper.setAcceleration(1000);

    while (!homed) {
        if (digitalRead(LIMIT_PIN) == HIGH) {
            stepper.stop();
            stepper.setCurrentPosition(0);
            homed = true;
        } else {
            stepper.setSpeed(-50);
            stepper.runSpeed();
        }
    }

    servoDrop();
}

void loop() {
    Bridge.provide("stepper", movePos);
}
