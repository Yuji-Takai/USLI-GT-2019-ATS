from enum import Enum
from constants import FULLSCALE, SUBSCALE
import math
from ats_math import inch2meter, feet2meter, oz2kg
class RocketType(Enum):
    '''
    Represents the rocket type
    '''
    SUBSCALE = 0
    FULLSCALE = 1

class RocketState(Enum):
    '''
    Represents the rocket state
    '''
    PRELAUNCH = 0
    MOTOR_ASCENT = 1
    COAST = 2
    DESCENT = 3
    GROUND = 4

class Rocket:
    '''
    Represents the rocket
    '''
    def __init__(self, rocket_type):
        self.motor_burnout_t = 0.0
        self.target_alt = 0.0
        self.diameter = 0.0
        self.fin_height = 0.0
        self.fin_thickness = 0.0
        self.fin_num = 0
        self.mass = 0.0
        self.drag_coeff = 1.0
        self.state = RocketState.PRELAUNCH

        if rocket_type == RocketType.SUBSCALE:
            self.motor_burnout_t = SUBSCALE['motor burnout time']
            self.target_alt = feet2meter(SUBSCALE['target altitude'])
            self.diameter = inch2meter(SUBSCALE['diameter'])
            self.fin_height = inch2meter(SUBSCALE['fin height'])
            self.fin_thickness = inch2meter(SUBSCALE['fin thickness'])
            self.fin_num = SUBSCALE['fin number']
            self.mass = oz2kg(SUBSCALE['mass'])
            self.drag_coeff = SUBSCALE['drag coefficient']
        elif rocket_type == RocketType.FULLSCALE:
            self.motor_burnout_t = FULLSCALE['motor burnout time']
            self.target_alt = feet2meter(FULLSCALE['target altitude'])
            self.diameter = inch2meter(FULLSCALE['diameter'])
            self.fin_height = inch2meter(FULLSCALE['fin height'])
            self.fin_thickness = inch2meter(FULLSCALE['fin thickness'])
            self.fin_num = FULLSCALE['fin number']
            self.mass = oz2kg(FULLSCALE['mass'])
            self.drag_coeff = FULLSCALE['drag coefficient']

        self.surface_area = self.rocket_area_without_ATS()

    def rocket_area_without_ATS(self):
        '''
        returns cross-sectional area of rocket without ATS flaps out
        radius: radius of rocket
        height: height of fin
        thickness: thickness of fin
        '''
        return ((self.diameter * 0.5) ** 2) * math.pi + self.fin_height * self.fin_thickness * self.fin_num

