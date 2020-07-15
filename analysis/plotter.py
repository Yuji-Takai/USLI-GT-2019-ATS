import matplotlib.pyplot as plt
import csv
from sensor_data import SensorData
from event import Event
from ats_math import pressure2alt, feet2meter, inch2meter, oz2kg, alt2rho
import math
from constants import STANDARD_GRAVITY, STEP_SIZE
from openrocket_data import OpenRocketData
from stratologger_data import StratoLoggerData
from analyzer import Analyzer
from rocket import RocketType
import argparse

class Plotter():
    '''
        Plots various data from a launch
    '''
    def __init__(self, rocket_type, launch_fname, openrocket_fname, stratologger_fname):
        self.analyzer = Analyzer(rocket_type, launch_fname, openrocket_fname, stratologger_fname)

    def plot(self, altitude, velocity, rotation, alt_prediction, drag_coefficient, acceleration):
        fig_num = 1
        if (altitude):
            plt.figure(fig_num)
            plt.title("Altitude graph")
            p1, = plt.plot(self.analyzer.t_sense, self.analyzer.alt_sense, color="r", label="SenseHAT altitude")
            p2, = plt.plot([self.analyzer.stratologger_data[i].time for i in range(len(self.analyzer.stratologger_data))], 
                [self.analyzer.stratologger_data[i].alt for i in range(len(self.analyzer.stratologger_data))], color="b", label="Stratologger altitude")
            plt.xlabel("time (s)")
            plt.ylabel("altitude (m)")
            plt.legend(handles=[p1, p2])
            fig_num += 1
        if (velocity):
            plt.figure(fig_num)
            plt.title("Velocity graph")
            p3, = plt.plot(self.analyzer.t_sense, self.analyzer.v_sense, color="r", label="SenseHAT velocity")
            p4, = plt.plot([self.analyzer.stratologger_data[i].time for i in range(len(self.analyzer.stratologger_data))], 
                [self.analyzer.stratologger_data[i].v for i in range(len(self.analyzer.stratologger_data))], color="b", label="Stratologger velocity")
            p5, = plt.plot(self.analyzer.t_sense, self.analyzer.v_sense_smooth, color="g", label="SenseHAT velocity smoothed")
            plt.xlabel("time (s)")
            plt.ylabel("velocity (m/s)")
            plt.legend(handles=[p3, p4, p5])
            fig_num += 1
        if (rotation):
            plt.figure(fig_num)
            plt.title("Rotation graph")
            p6, = plt.plot(self.analyzer.t_sense, [math.sin(self.analyzer.sense_hat_data[i].pitch / 180 * math.pi) for i in range(len(self.analyzer.sense_hat_data))], color="r", label="Pitch")
            p7, = plt.plot(self.analyzer.t_sense, [math.sin(self.analyzer.sense_hat_data[i].roll / 180 * math.pi) for i in range(len(self.analyzer.sense_hat_data))], color="b", label="roll")
            p8, = plt.plot(self.analyzer.t_sense, [math.sin(self.analyzer.sense_hat_data[i].yaw / 180 * math.pi) for i in range(len(self.analyzer.sense_hat_data))], color="g", label="yaw")
            plt.xlabel("time (s)")
            plt.ylabel("Sine of angle")
            plt.axvline(x=self.analyzer.t_sense[self.analyzer.events["Apogee"]], color="k", linestyle="-")
            plt.legend(handles=[p6, p7, p8], bbox_to_anchor=(1,1), loc="upper left")
            plt.tight_layout()
            fig_num += 1
        if (alt_prediction):
            plt.figure(fig_num)
            plt.title("Altitude prediction")
            p9, = plt.plot(self.analyzer.t_sense, self.analyzer.alt_sense, color="r", label="Actual Altitude")
            p10, = plt.plot(self.analyzer.t_sense[:self.analyzer.events["Apogee"]], self.analyzer.alt_pred_smooth, color="b", label="Predicted Altitude without ATS")
            p11, = plt.plot(self.analyzer.t_sense[:self.analyzer.events["Apogee"]], self.analyzer.alt_pred_with_ATS_smooth, color="g", label="Predicted Altitude with ATS")
            plt.xlabel("time (s)")
            plt.ylabel("Altitude (m)")
            p12 = plt.axhline(y=feet2meter(4800), color="k", linestyle="-", label="Target Apogee Altitude")
            plt.axhline(y=feet2meter(4800 + 10), color="k", linestyle="dotted")
            plt.axhline(y=feet2meter(4800 - 10), color="k", linestyle="dotted")
            plt.legend(handles=[p9, p10, p11, p12])
            fig_num += 1
        if (drag_coefficient):
            plt.figure(fig_num)
            plt.title("Drag Coefficient")
            p13, = plt.plot(self.analyzer.t_sense[self.analyzer.events["Motor burnout"]:self.analyzer.events["Apogee"]], self.analyzer.Cd_sense, color="r", label="Cd from Sense HAT")
            p14, = plt.plot([self.analyzer.openrocket_data[i].time for i in range(len(self.analyzer.openrocket_data))], 
                [self.analyzer.openrocket_data[i].cd for i in range(len(self.analyzer.openrocket_data))], color="b", label="Cd from OpenRocket")
            plt.axvline(x=self.analyzer.t_sense[self.analyzer.events["Apogee"]], color="k", linestyle="-")
            plt.legend(handles=[p13, p14])
            plt.xlabel("time (s)")
            plt.ylabel("Coefficient of Drag")
            fig_num += 1
        if (acceleration):
            plt.figure(fig_num)
            plt.title("Acceleration")
            p15, = plt.plot([self.analyzer.openrocket_data[i].time for i in range(len(self.analyzer.openrocket_data))], 
                [self.analyzer.openrocket_data[i].a_total for i in range(len(self.analyzer.openrocket_data))], color="r", label="Total Acceleration OpenRocket")
            p16, = plt.plot([self.analyzer.openrocket_data[i].time for i in range(len(self.analyzer.openrocket_data))], 
                [self.analyzer.openrocket_data[i].az for i in range(len(self.analyzer.openrocket_data))], color="b", label="Vertical Acceleration OpenRocket")
            p17, = plt.plot(self.analyzer.t_sense, [self.analyzer.sense_hat_data[i].az - 1 for i in range(len(self.analyzer.sense_hat_data))], color="g", label="Vertical Acceleration SenseHAT")
            plt.xlabel("time (s)")
            plt.ylabel("Acceleration (G)")
            plt.axvline(x=self.analyzer.t_sense[self.analyzer.events["Apogee"]], color="k", linestyle="-")
            plt.legend(handles=[p15, p16, p17])
            plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Choose the rocket type')
    parser.add_argument('-s', '--subscale', action="store_true", help="Choose if for subscale rocket")
    parser.add_argument('-f', '--fullscale', action="store_true", help="Choose if for fullscale rocket")
    parser.add_argument('-a', '--all', action="store_true", help="Choose if plotting all")
    parser.add_argument('-alt', '--altitude', action="store_true", help="Choose if plotting altitude comparison")
    parser.add_argument('-v', '--velocity', action="store_true", help="Choose if plotting velocity comparison")
    parser.add_argument('-r', '--rotation', action="store_true", help="Choose if plotting rotation data")
    parser.add_argument('-p', '--prediction', action="store_true", help="Choose if plotting altitude prediction at each timestamp")
    parser.add_argument('-d', '--drag', action="store_true", help="Choose if plotting drag coefficient comparison")
    parser.add_argument('-accel', '--acceleration', action="store_true", help="Choose if plotting acceleration comparison")
    args = parser.parse_args()
    if args.subscale:
        plotter = Plotter(RocketType.SUBSCALE,  "./data/fullscale/2020_3_7_11_10.csv", "./data/fullscale/OpenRocket_sim_data.csv", "./data/fullscale/Alt1FlightData.csv")
    if args.fullscale:
        plotter = Plotter(RocketType.FULLSCALE,  "./data/fullscale/2020_3_7_11_10.csv", "./data/fullscale/OpenRocket_sim_data.csv", "./data/fullscale/Alt1FlightData.csv")
    
    if args.all:
        plotter.plot(True, True, True, True, True, True)
    else:
        plotter.plot(args.altitude, args.velocity, args.rotation, args.prediction, args.drag, args.acceleration)
