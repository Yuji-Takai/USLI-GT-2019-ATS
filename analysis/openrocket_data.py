class OpenRocketData():
    '''
    Represents the data simulated by OpenRocket

    time: float
        time from take off in seconds
    alt: float
        altitude in feet
    vz: float
        vertical velocity in ft/s
    az: float
        vertical acceleration in G
    a_total: float
        total acceleration in G
    rocket_mass: float
        rocket mass in oz
    propellant_mass: float
        propellant mass in oz
    thrust: float
        thrust in N
    drag: float
        thrust in N
    cd: float
        coefficient of drag
    '''
    def __init__(self, time, alt, vz, az, a_total, rocket_mass, propellant_mass, thrust, drag, cd):
        self.time = time
        self.alt = alt
        self.vz = vz
        self.az = az
        self.a_total = a_total
        self.rocket_mass = rocket_mass
        self.propellant_mass = propellant_mass
        self.thrust = thrust
        self.drag = drag
        self.cd = cd
