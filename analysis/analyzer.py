import matplotlib.pyplot as plt
import csv
from sensor_data import SensorData
from event import Event
from ats_math import pressure2alt, feet2meter, inch2meter, oz2kg, alt2rho
import math
from constants import STANDARD_GRAVITY, STEP_SIZE, ATS_FULLSCALE
from openrocket_data import OpenRocketData
from stratologger_data import StratoLoggerData
from rocket import RocketType, Rocket
class Analyzer:
    '''
        Analyzes the launch data collected from Sense HAT and StratoLogger CF 
        and compares those data with OpenRocket simulation data

        rocket: Rocket
            rocket used during the launch (either fullscale or subscale)
        sense_hat_data: list(SensorData)
            list of sensor data from Sense HAT
        events: dict(str, int)
            mapping of events to index in sense_hat_data when they occurred
        t_sense: list(float)
            list of timestamps of Sense HAT data
        openrocket_data: list(OpenRocketData)
            list of simulation data points from OpenRocket
        stratologger_data: list(StratoLoggerData)
            list of sensor data from StratoLogger CF
        base_alt: float
            altitude of launch site from mean sea level, needed for offsetting the altitude data
        alt_sense: list(float)
            list of altitude data computed from Sense HAT pressure data
        v_sense: list(float)
            list of velocity data computed by using finite difference approximation on altitude data
        v_sense_smooth: list(float)
            list of velocity data computed by averaging each data point in v_sense with 9 proceeding data points
        alt_pred_with_ATS: list(float)
            list of predicted apogee altitude with ATS fully actuated at each timestamp
        alt_pred_with_ATS_smooth: list(float)
            list of smoothened apogee altitude predictions with ATS fully actuated
        alt_pred: list(float)
            list of predicted apogee altitude without ATS at each timestamp
        alt_pred_smooth: list(float)
            list of smoothened apogee altitude predictions without ATS
        Cd_sense: list(float)
            list of coefficient of drag computed from Sense HAT sensor data
    '''
    def __init__(self, rocket_type, launch_fname, openrocket_fname, stratologger_fname):
        self.rocket = Rocket(rocket_type)
        self.ats_total_area = inch2meter(inch2meter(ATS_FULLSCALE["config6"][1] * ATS_FULLSCALE["flap number"]))
        self.read_launch_data(launch_fname)
        self.read_openrocket_data(openrocket_fname)
        self.read_stratologger_data(stratologger_fname)
        self.compute_base_alt()
        self.compute_alt_sense()
        self.compute_v_sense()
        self.v_sense_smooth = self.smooth(self.v_sense)
        self.alt_pred_with_ATS = [self.predict(self.v_sense[i], self.alt_sense[i], self.rocket.rocket_area_without_ATS() + self.ats_total_area) for i in range(self.events["Apogee"])]
        self.alt_pred_with_ATS_smooth = self.smooth(self.alt_pred_with_ATS)
        self.alt_pred = [self.predict(self.v_sense[i], self.alt_sense[i], self.rocket.rocket_area_without_ATS()) for i in range(self.events["Apogee"])]
        self.alt_pred_smooth = self.smooth(self.alt_pred)
        self.Cd_sense = [self.compute_Cd(self.sense_hat_data[i].az, self.alt_sense[i], self.v_sense_smooth[i]) for i in range(self.events["Motor burnout"], self.events["Apogee"])]
        print(self.rocket.rocket_area_without_ATS())
        
    def read_launch_data(self, launch_fname):
        '''
            Reads in Sense HAT data logged during launch
        '''
        self.sense_hat_data = []
        self.events = {}
        self.t_sense = []
        with open(launch_fname, 'r') as f:
            reader = csv.reader(f, delimiter=",")
            next(reader)
            for i, row in enumerate(reader):
                self.sense_hat_data.append(SensorData(time=float(row[0]), 
                    ax=float(row[1]), ay=float(row[2]), az=float(row[3]), 
                    pitch=float(row[4]), roll=float(row[5]), yaw=float(row[6]), 
                    temp=float(row[7]), pressure=float(row[8])))
                self.t_sense.append(float(row[0]))
                if row[9] == "Event.TAKE_OFF":
                    self.sense_hat_data[-1].event = Event.TAKE_OFF
                    self.events["Take off"] = i
                elif row[9] == "Event.MOTOR_BURNOUT":
                    self.sense_hat_data[-1].event = Event.MOTOR_BURNOUT
                    self.events["Motor burnout"] = i
                elif row[9] == "Event.APOGEE":
                    self.sense_hat_data[-1].event = Event.APOGEE
                    self.events["Apogee"] = i
                elif row[9] == "Event.TOUCH_DOWN":
                    self.sense_hat_data[-1].event = Event.TOUCH_DOWN
                    self.events["Touch Down"] = i

    def read_openrocket_data(self, openrocket_fname):
        '''
            Reads in OpenRocket simulation data
        '''
        self.openrocket_data = []
        with open(openrocket_fname, 'r') as f:
            reader = csv.reader(f, delimiter=",")
            next(reader)
            for row in reader:
                self.openrocket_data.append(OpenRocketData(float(row[0]), float(row[1]), 
                    float(row[2]), float(row[3]) / 32.17405, float(row[4]) / 32.17405, float(row[5]), float(row[6]),
                    float(row[7]), float(row[8]), (float(row[9]) if row[9] != "NaN" else 0)))

    def read_stratologger_data(self, stratologger_fname):
        '''
            Reads in StratoLogger CF data
        '''
        self.stratologger_data = []
        with open(stratologger_fname, 'r') as f:
            reader = csv.reader(f, delimiter=",")
            next(reader)
            for row in reader:
                self.stratologger_data.append(StratoLoggerData(float(row[0]),
                    feet2meter(float(row[1])), feet2meter(float(row[2])), float(row[3]), float(row[4])))

    def compute_base_alt(self):
        '''
            Computes the altitude of launch site from mean sea level
        '''
        total = 0
        for i in range(5):
            total += self.sense_hat_data[i].pressure
        self.base_alt = pressure2alt(total/5)

    def compute_alt_sense(self):
        '''
            Computes altitude data from Sense HAT pressure data
        '''
        self.alt_sense = [pressure2alt(self.sense_hat_data[i].pressure) - self.base_alt for i in range(len(self.sense_hat_data))]

    def compute_v_sense(self):
        '''
            Computes vertical velocity data by using finite difference approximation on altitude data
        '''
        self.v_sense = [0.0]
        for i in range(1, len(self.alt_sense)):
            self.v_sense.append((self.alt_sense[i] - self.alt_sense[i - 1])/(self.t_sense[i] - self.t_sense[i - 1]))

    def smooth(self, arr):
        '''
            Smoothens given list by averaging each data point with 9 proceeding data points
        '''
        smooth = []
        for i in range(len(arr)):
            offset = 9 if i > 9 else i
            total = sum(arr[i-offset:i + 1])
            smooth.append(total/(offset + 1))
        return smooth

    def predict(self, v0, alt0, A):
        '''
            Predicts the apogee altitude with the given initial velocity, initial altitude and projected area
        '''
        def ode(g, A, Cd, rho, m, v):
            '''
                Returns the acceleration of the launch vehicle during the coast state
                the launch vehicle's equation of motion is simplified to be only the sum of weight and drag
            '''
            return -g - ((A * Cd * rho *(v ** 2) * 0.5) / m)
        
        v_n = v0
        alt_n = alt0
        rho_n = alt2rho(alt0 + self.base_alt)
        while (v_n >= 0):
            k1 = ode(STANDARD_GRAVITY, A, self.rocket.drag_coeff, rho_n, self.rocket.mass, v_n)
            k2 = ode(STANDARD_GRAVITY, A, self.rocket.drag_coeff, rho_n, self.rocket.mass, v_n + k1 * 0.5)
            k3 = ode(STANDARD_GRAVITY, A, self.rocket.drag_coeff, rho_n, self.rocket.mass, v_n + k2 * 0.5)
            k4 = ode(STANDARD_GRAVITY, A, self.rocket.drag_coeff, rho_n, self.rocket.mass, v_n + k3)
            v_n += STEP_SIZE * (k1 + 2.0 * k2 + 2.0 * k3 + k4)/6.0
            alt_n += STEP_SIZE * v_n
            rho_n = alt2rho(alt_n + self.base_alt)
        return alt_n

    def compute_Cd(self, az, alt, v):
        '''
            Computes the coefficient of drag given vertical acceleration, altitude, and vertical velocity
        '''
        return -2 * (self.rocket.mass * (az - 1) * STANDARD_GRAVITY + self.rocket.mass * STANDARD_GRAVITY) / (alt2rho(alt) * 0.0194 * ((v - 25) ** 2)) if v != 0 else 0  # TODO better velocity value should be used
if __name__ == "__main__":
    a = Analyzer(RocketType.FULLSCALE, "./data/fullscale/2020_3_7_11_10.csv", "./data/fullscale/OpenRocket_sim_data.csv", "./data/fullscale/Alt1FlightData.csv")
    print(a.smooth([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]))
    