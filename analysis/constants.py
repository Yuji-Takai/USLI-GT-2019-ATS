STANDARD_GRAVITY = 9.80665 # standard gravity (m/s^2)
PRESSURE_MSL = 1013.25 # air pressure at mean sea level (hPa)
LAPSE_RATE = -0.0065 # temperature lapse rate between 0 m and 11,000 m (K/m)
TEMP_MSL = 288.15 # temperature at mean sea level (K)
GAS_CONSTANT = 8.31432 # Gas constant (J/(mol*K))
MOLAR_MASS = 0.0289644 # molar mass of air upto 90 km (kg/mol)
RHO_MSL = 1.225 # air density at mean sea level (kg/m^3)
ALT_CONST = TEMP_MSL/LAPSE_RATE # used for pressure to altitude conversion
EXP = (LAPSE_RATE * GAS_CONSTANT) / (MOLAR_MASS * STANDARD_GRAVITY) # used for pressure to altitude conversion
EXP_INVERSE = (MOLAR_MASS * STANDARD_GRAVITY) / (LAPSE_RATE * GAS_CONSTANT) # used for altitude to density conversion

TAKEOFF_DETECTION_THRESHOLD = 5 # total acceleration threshold to detect take off (G)
PRELAUNCH_BUFFER_SIZE = 5 # size of the buffer storing the prelaunch data

STEP_SIZE = 0.01 # step size for Runge Kutta

FULLSCALE = {'motor burnout time': 2.3,         # motor burnout time for AeroTech L2200 (s)
    'target altitude': 4800,                    # target apogee altitude (ft)
    'diameter': 6.188,                          # rocket radius (in)
    'fin height': 12,                           # fin height (in)
    'fin thickness': 0.25,                      # fin thickness (in)
    'fin number': 4,                            # number of fins
    'mass': 662,                                # rocket mass (oz)
    'drag coefficient': 0.665                   # drag coefficient - TODO: make a feedback loop to derive drag coefficient
    }

SUBSCALE = {'motor burnout time': 1.6,          # motor burnout time for AeroTech J800 (s)
    'target altitude': 2500,                    # target apogee altitude (ft)
    'diameter': 4.024,                          # rocket radius (in)
    'fin height': 4.33,                         # fin height (in)
    'fin thickness': 0.165,                     # fin thickness (in)
    'fin number': 4,                            # number of fins
    'mass': 242,                                # rocket mass (oz)
    'drag coefficient': 0.665                   # drag coefficient - TODO: make a feedback loop to derive drag coefficient
    }

ATS_FULLSCALE = {'flap number': 3,
    'config1': (0, 0),
    'config2': (60, 0.2703),
    'config3': (120, 0.9114),
    'config4': (180, 1.5244),
    'config5': (240, 2.0955),
    'config6': (300, 2.6336)
    }