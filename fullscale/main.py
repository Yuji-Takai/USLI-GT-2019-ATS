from sensor import Sensor
from calculator import Calculator
from actuator import Actuator
from logger import Logger
from rocket import Rocket, RocketType, RocketState
from event import Event
from datetime import datetime
from circular_queue import CircularQueue
from constants import TAKEOFF_DETECTION_THRESHOLD, PRELAUNCH_BUFFER_SIZE
import argparse
class Main:
    def __init__(self, rocket):
        self.sensor = Sensor()
        self.calculator = Calculator(rocket)
        self.actuator = Actuator()
        today = datetime.now()
        self.logger = Logger("{}_{}_{}_{}:{}.csv".format(today.year, today.month, today.day, today.hour, today.minute))
        self.rocket = rocket
        self.start_time = today

    def run(self):
        prelaunch_buffer = CircularQueue(PRELAUNCH_BUFFER_SIZE)
        while (self.rocket.state != RocketState.GROUND):
            data = self.sensor.getData()
            if (self.rocket.state == RocketState.PRELAUNCH):
                # PRELAUNCH state
                prelaunch_buffer.add(data) 
                # Checking if the launch vehicle took off
                if data.total_accel() > TAKEOFF_DETECTION_THRESHOLD:
                    arr = prelaunch_buffer.toArray()
                    self.start_time = arr[0].time # setting start time of the launch vehicle
                    arr[-1].event = Event.TAKE_OFF # the latest data will be marked as TAKE_OFF
                    total = 0.0
                    for point in arr:
                        point.normalize(self.start_time)
                        self.logger.write(point)
                        total += point.pressure
                    self.rocket.state = RocketState.MOTOR_ASCENT
                    self.calculator.setBaseAlt(total/PRELAUNCH_BUFFER_SIZE) # base altitude is based on average pressure 
                    print("moving to motor ascent state")
            elif (self.rocket.state == RocketState.MOTOR_ASCENT):
                # MOTOR_ASCENT state
                data.normalize(self.start_time)
                self.calculator.compute(data)
                # Checking if the motor burned up by checking the duration since take off
                if data.time >= self.rocket.motor_burnout_t + 1:
                    self.rocket.state = RocketState.COAST
                    data.event = Event.MOTOR_BURNOUT
                    print("moving to coast state")
                self.logger.write(data)
            elif (self.rocket.state == RocketState.COAST):
                # COAST state
                data.normalize(self.start_time)
                self.calculator.compute(data)
                if self.calculator.predict() > self.rocket.target_alt:
                    self.actuator.actuate()
                else:
                    self.actuator.retract()
                print("Current velocity: {}".format(self.calculator.v_current()))
                # Checking if velocity of the launch vehicle is negative
                if self.calculator.v_current() < 0:
                    data.event = Event.APOGEE
                    self.actuator.retract()
                    self.rocket.state = RocketState.DESCENT
                    print("moving to descent state")
                self.logger.write(data)
            elif (self.rocket.state == RocketState.DESCENT):
                # DESCENT state
                data.normalize(self.start_time)
                self.calculator.compute(data)
                print("Current velocity: {}".format(self.calculator.v_current()))
                # TO DO need to make the detection of landing better since after apogee, there will be a time when the velocity is greater than -2
                if self.calculator.v_current() > -2:
                    data.event = Event.TOUCH_DOWN
                    self.rocket.state = RocketState.GROUND
                    print("moving to ground state")
                self.logger.write(data)
        # GROUND state
        for _ in range(5):
            data = self.sensor.getData()
            data.normalize(self.start_time)
            self.logger.write(data)
        self.logger.purge()

        self.shutdown()

    def shutdown(self):
        print("shutdown")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Choose the rocket type')
    parser.add_argument('-s', '--subscale', action="store_true", help="Choose if for subscale rocket")
    parser.add_argument('-f', '--fullscale', action="store_true", help="Choose if for fullscale rocket")
    args = parser.parse_args()
    if args.subscale:
        Main(Rocket(RocketType.SUBSCALE)).run()
    else:
        Main(Rocket(RocketType.FULLSCALE)).run()

