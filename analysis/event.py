from enum import Enum
class Event(Enum):
    '''
    Represents the event occurred during the flight
    '''
    DEFAULT = 0
    TAKE_OFF = 1
    MOTOR_BURNOUT = 2
    APOGEE = 3
    TOUCH_DOWN = 4
