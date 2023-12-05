#define DEBUGSERIAL true

int speedPin = 9;      // H-bridge enable pin for speed control
int motor1APin = 7;     // H-bridge leg 1 
int motor2APin = 8;     // H-bridge leg 2 
int ledPin = 13;       // status LED
int ENA = 2; // pin D2 for channel A of encoder
int ENB = 4; // pin D4 for channel B of encoder
int buzzer = 3; // pwm pin D3 for buzzer

int motor_speed = 255; // value for motor speed
int encoderCount = 0;
int motor_enable = 1;

int limit = 1; //233; // need to figure this shit out
int lastLimit = limit;
// 280 pulses per revolution 
// 280 / 360 * 300 = 233.33 --> pulse for limiting the motion to 300 degrees

// auto shutdown
int lastEncoderCount = encoderCount;
int lastEncoderChangeTimestamp = millis();
int lastEncoderChangeMsAgo = 0;
int stallThresholdMs = 500;

// uart stuff
String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete

// test string for heartbeat
String heartbeat = "GOOD";

// test string for activate
String activate = "ACT";
// test string for retract
String retract = "RET";


void setup() {
  // put your setup code here, to run once:
  if (DEBUGSERIAL) {
    Serial.begin(9600);
  }
  pinMode(speedPin, OUTPUT);  
  pinMode(motor1APin, OUTPUT);   
  pinMode(motor2APin, OUTPUT);   
  pinMode(ledPin, OUTPUT);

  pinMode(ENA, INPUT);
  pinMode(ENB, INPUT);

  attachInterrupt(digitalPinToInterrupt(ENA), readEncoder, FALLING);
}

void loop() {
  digitalWrite(ledPin, HIGH);
  // put your main code here, to run repeatedly:
  motorLogic();
  if (DEBUGSERIAL) {
    int sensor1 = digitalRead(ENA);
    //Serial.print("sensor1: ");
    //Serial.print(sensor1);
    //Serial.print(", ");
    int sensor2 = digitalRead(ENB);
    //Serial.print("sensor2: ");
    //Serial.print(sensor2);
    //Serial.println(", ");
  }

  if (encoderCount == lastEncoderCount && limit == lastLimit) {
    lastEncoderChangeMsAgo = millis() - lastEncoderChangeTimestamp;
  } else {
    lastEncoderChangeTimestamp = millis();
    lastEncoderChangeMsAgo = millis() - lastEncoderChangeTimestamp;
    lastLimit = limit;  // we are moving; we have a good limit
  }

  if (lastEncoderChangeMsAgo > stallThresholdMs) {
    motor_enable = false;
  } else {
    motor_enable = true;
  }

  noTone(buzzer);

  updateSerialMessage();

  handleUART();
  

  delay(20);
}

/*
  SerialEvent occurs whenever a new data comes in the hardware serial RX. This
  routine is run between each time loop() runs, so using delay inside loop can
  delay response. Multiple bytes of data may be available.
*/
void updateSerialMessage() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}


void handleUART() {

  

  if (stringComplete) {
    //Serial.print("handle uart: ");
    //Serial.println(inputString);
    
    boolean foundGood = true;
    boolean foundActivate = true;
    boolean foundRetract = true;

    for (int i = 0; i < 3; i++) {
      //Serial.print(inputString[i]);
      //Serial.print(" -- ");
      //Serial.println(heartbeat[i]);
      if (inputString[i] != heartbeat[i]) {
        foundGood = false;
      }
      if (inputString[i] != activate[i]) {
        foundActivate = false;
      }
      if (inputString[i] != retract[i]) {
        foundRetract = false;
      }
    }

    if (foundGood == true) {
      tone(buzzer, 2000, 1000);
    }

    if (foundActivate == true) {
      tone(buzzer, 1000, 100);
      activateFlaps();
    }

    if (foundRetract == true) {
      tone(buzzer, 500, 100);
      retractFlaps();
    }

    // clear the string:
    inputString = "";
    stringComplete = false;
  }
  
}

void activateFlaps() {
  limit = 233;
}

void retractFlaps() {
  limit = 1;
}



void motorLogic() {
  if (motor_enable == false) {
    brake();
    tone(buzzer, 100, 100);
  } else if (encoderCount < limit && !inErrorRange(encoderCount, limit, 10)) {
    drive(motor_speed);
  } else if (encoderCount > limit && !inErrorRange(encoderCount, limit, 10)) {
    drive(-motor_speed);
  } else {
    brake();
  }
}

bool inErrorRange(int a, int b, int range) {
  int tmp = a - b;
  if (tmp < 0) {
    tmp = -tmp;
  }
  if (tmp < range) {
    Serial.println("in range");
    return true;
  }
  return false;
}

void drive(int motorspeed) {
  if (motorspeed > 0) {
    // put motor in forward motion    
    digitalWrite(motor1APin, LOW);   
    // set leg 1 of the H-bridge low    
    digitalWrite(motor2APin, HIGH);  
    digitalWrite(speedPin, motorspeed); 
  } else {
    digitalWrite(motor1APin, HIGH);
    digitalWrite(motor2APin, LOW);
    digitalWrite(speedPin, motorspeed);
  }
}

void brake() {
  Serial.print("brake");
  digitalWrite(motor1APin, LOW);
  digitalWrite(motor2APin, LOW);
}


void readEncoder() {
  Serial.println(encoderCount);
  if (digitalRead(ENB)) {
    encoderCount--;
  } else {
    encoderCount++;
  }
  motorLogic();
}