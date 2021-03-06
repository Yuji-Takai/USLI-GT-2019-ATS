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
import time
class Main:
    '''
    Main class of the ATS software
    '''
    def __init__(self, rocket):
        self.sensor = Sensor()
        self.calculator = Calculator(rocket)
        self.actuator = Actuator()
        today = datetime.now()
        self.logger = Logger("{}_{}_{}_{}:{}.csv".format(today.year, today.month, today.day, today.hour, today.minute))
        self.rocket = rocket
        self.start_time = today
        self.apogee_time = 0
        self.ats_state = 0 # 0 for closed, 1 for open, 2 for transition from closed to open, -1 for transition from open to closed
        self.base_time = 0
        self.sensor.sense.show_message("OK", text_colour=(0,255,0))

    def run(self):
        prelaunch_buffer = CircularQueue(PRELAUNCH_BUFFER_SIZE)
        print("moving to prelaunch state")
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
                    self.base_time = data.time
                self.logger.write(data)
            elif (self.rocket.state == RocketState.COAST):
                # COAST state
                data.normalize(self.start_time)
                self.calculator.compute(data)

                if self.ats_state == 0 and (data.time - self.base_time >= 1):
                    # if been in closed state for more than 1 second, start opening the flaps
                    self.ats_state = 2
                    self.base_time = data.time
                    self.actuator.actuate()
                    data.command = "ACTUATE"
                elif self.ats_state == 1 and (data.time - self.base_time >= 1):
                    self.ats_state = -1 
                    self.base_time = data.time
                    self.actuator.retract()
                    data.command = "RETRACT"
                elif self.ats_state == 2:
                    if (data.time - self.base_time < 2):
                        self.actuator.actuate()
                    else:
                        self.ats_state = 1
                        self.base_time = data.time
                        data.command = "COMPLETED ACTUATION"
                else:
                    if (data.time - self.base_time < 2):
                        self.actuator.retract()
                    else:
                        self.ats_state = 0
                        self.base_time = data.time
                        data.command = "COMPLETED RETRACTION"
                        

                    


                # if self.calculator.predict() > self.rocket.target_alt:
                #     self.actuator.actuate()
                # else:
                #     self.actuator.retract()
                print("Current velocity: {}".format(self.calculator.v_current()))
                # Checking if velocity of the launch vehicle is negative
                if self.calculator.v_current() < 0:
                    data.event = Event.APOGEE
                    self.actuator.retract()
                    self.rocket.state = RocketState.DESCENT
                    self.apogee_time = data.time
                    print("moving to descent state")
                self.logger.write(data)
            elif (self.rocket.state == RocketState.DESCENT):
                # DESCENT state
                data.normalize(self.start_time)
                self.calculator.compute(data)
                print("Current velocity: {}".format(self.calculator.v_current()))
                # Detect landing when velocity is be greated than -2 m/s and it has been at least 5 seconds after apogee
                if self.calculator.v_current() > -2 and data.time - self.apogee_time > 5:
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
    parser.add_argument('-t', '--test', action="store_true", help="Choose if testing")
    args = parser.parse_args()
    if not args.test:
        time.sleep(60)
    if args.subscale:
        Main(Rocket(RocketType.SUBSCALE)).run()
    else:
        Main(Rocket(RocketType.FULLSCALE)).run()

