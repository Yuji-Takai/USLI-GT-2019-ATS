from circular_queue import CircularQueue
from constants import STANDARD_GRAVITY, STEP_SIZE
from ats_math import pressure2alt, alt2rho, fda
class Calculator:
    def __init__(self, rocket):
        self.data_buffer = CircularQueue(10)
        self.alt_buffer = CircularQueue(10)
        self.v_buffer = CircularQueue(10)
        self.rocket = rocket
        self.base_alt = 0

    def setBaseAlt(self, pressure):
        self.base_alt = pressure2alt(pressure)

    def compute(self, data):
        self.data_buffer.add(data)
        self.alt_buffer.add(pressure2alt(data.pressure))
        if (self.v_buffer.size() == 0):
            self.v_buffer.add(0)
        else:
            curr_alt = self.alt_buffer.get_last()
            prev_alt = self.alt_buffer.get_second_last()
            curr_time = data.time
            prev_time = self.data_buffer.get_second_last().time
            self.v_buffer.add(fda(prev_alt, curr_alt, prev_time, curr_time))

    def ode(self, g, A, Cd, rho, m, v):
        return -g - ((A * Cd * rho *(v ** 2) * 0.5) / m)

    def predict(self):
        v_n = self.v_buffer.average()
        alt_n = self.alt_buffer.average()
        rho_n = alt2rho(alt_n)

        while (v_n > 0):
            k1 = self.ode(STANDARD_GRAVITY, self.rocket.surface_area, self.rocket.drag_coeff, rho_n, self.rocket.mass, v_n)
            k2 = self.ode(STANDARD_GRAVITY, self.rocket.surface_area, self.rocket.drag_coeff, rho_n, self.rocket.mass, v_n + k1 * 0.5)
            k3 = self.ode(STANDARD_GRAVITY, self.rocket.surface_area, self.rocket.drag_coeff, rho_n, self.rocket.mass, v_n + k2 * 0.5)
            k4 = self.ode(STANDARD_GRAVITY, self.rocket.surface_area, self.rocket.drag_coeff, rho_n, self.rocket.mass, v_n + k3)
            v_n = v_n + STEP_SIZE * (k1 + 2.0 * k2 + 2.0 * k3 + k4)/6.0
            alt_n = alt_n + STEP_SIZE * v_n
            rho_n = alt2rho(alt_n + self.base_alt)

        return alt_n

    def v_current(self):
        return self.v_buffer.average()
