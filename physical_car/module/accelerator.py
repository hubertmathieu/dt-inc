import numpy as np

class Accelerator:

    def __init__(self, accel, speed):
        self._max_accel = accel
        self._max_speed = speed

    def speed_to_accel(self, last_speed, interval, forward=False):
        # ** comment savoir le temps que la loop présente se termine
        accel = (self._max_accel / interval)

        next_speed = last_speed + accel if forward else last_speed - accel

        if np.abs(next_speed) > np.abs(self._max_speed):
            next_speed = self._max_speed if forward else -self._max_speed

        return next_speed

    def speed_to_deccel(self, last_speed, interval, forward=False):

        accel = (self._max_accel / interval)

        if forward:
            next_speed = last_speed - accel
            if next_speed <= 0:
                return 0
        else:
            next_speed = last_speed + accel
            if next_speed >= 0:
                return 0
    @property
    def max_speed(self):
        return self._max_speed

    @max_speed.setter
    def max_accel(self, value):
        self._max_speed = value

    @property
    def max_accel(self):
        return self._max_accel

    @max_accel.setter
    def max_accel(self, value):
        self._max_accel = value
