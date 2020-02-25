import math
from constants import ALT_CONST, PRESSURE_MSL, RHO_MSL, TEMP_MSL, LAPSE_RATE, EXP, EXP_INVERSE

def inch2meter(inch):
    '''
    converts inches to meters
    inch: length in inches
    '''
    return inch * 0.0254

def feet2meter(feet):
    '''
    converts feet to meters
    feet: length in feet
    '''
    return feet * 0.3048

def oz2kg(oz):
    '''
    converts ounces to kilograms
    oz: mass in ounces
    '''
    return 0.028349523125 * oz

def pressure2alt(pressure):
    '''
    returns the altitude (from MSL) based on air pressure using US standard atmosphere
    pressure: pressure (hPa) of surrounding air
    '''
    return ALT_CONST * ((pressure/PRESSURE_MSL) ** (-EXP) - 1)

def alt2rho(alt):
    '''
    returns the air density based on altitude using US standard atmosphere
    alt: altitude (m) from MSL
    '''
    return RHO_MSL * ((TEMP_MSL/(TEMP_MSL + LAPSE_RATE * alt)) ** (EXP_INVERSE + 1))

def fda(y1, y2, t1, t2):
    '''
    returns derivative using finite difference approximation i.e. (y2 - y1) / (t2 - t1)
    '''
    return (y2 - y1)/(t2 - t1)