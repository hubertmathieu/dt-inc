import numpy as np

class Accelerator:

    def __init__(self, accel, goal_speed, interval, max_speed):
        self._max_accel = accel
        self._goal_speed = goal_speed
        self._interval = interval
        self._max_speed = max_speed

    # retourne la prochaine vitesse 
    def get_next_speed(self, last_speed):
        accel_per_clk = self._max_accel * self._interval

        if (last_speed < self.goal_speed):
            next_speed = last_speed + accel_per_clk
            if (next_speed > self.goal_speed):
                next_speed = self.goal_speed
                
        elif (last_speed > self.goal_speed):
            next_speed = last_speed - accel_per_clk
            if (next_speed < self._goal_speed):
                next_speed = self._goal_speed
        else:
            next_speed = last_speed

        return next_speed

    # si la decceleration devrait commencer
    def determine_stopping_dist(self, obstacle_distance, last_speed):
        if (last_speed != 0):
            dist_to_stop_cm = ((last_speed ** 2) / (2*self.max_accel)) * 100
                
            return np.abs(dist_to_stop_cm) >= obstacle_distance
        else:
            return False
        
    def get_speeds_to_accel(self):
        accel_per_clk = self._max_accel * self._interval

        return np.linspace(0, self._goal_speed, int(self._goal_speed / accel_per_clk))
        

    # atteindre 0 de vitesse
    def get_stop_speeds_list(self, last_speed):
        accel_per_clk = self._max_accel * self._interval

        return np.linspace(last_speed, 0, int(last_speed / accel_per_clk))

    # retourne une liste des vitesse pour un parcours de distance x (début: 0m/s, fin: 0m/s)
    def get_speeds_list_for_travel(self, distance, backward=True):
        max_speed_in_course = np.sqrt(distance * self._max_accel)
        accel_per_clk = self._max_accel * self._interval

        total_movements = int(2 * (max_speed_in_course) / accel_per_clk)

        # vérifier vitesse maximal du parcours
        # !! vréfier à partir constance 
        if (max_speed_in_course > self._max_speed):
            max_speed_in_course = self._max_speed

        # créer accel and deccel mouvements
        accel = np.linspace(0, max_speed_in_course, max_speed_in_course / accel_per_clk)
        deccel = np.linspace(max_speed_in_course, 0, max_speed_in_course / accel_per_clk)

        # créer mouvements de vitesse constante
        plateau_length = int(total_movements - len(accel) - len(deccel))
        plateau = np.empty(plateau_length, dtype=np.int)
        plateau = np.ones(plateau_length) * max_speed_in_course

        speeds = np.concatenate([accel, plateau, deccel])
        
        return -1 * speeds if backward else speeds
        
    @property
    def goal_speed(self):
        return self._goal_speed

    @goal_speed.setter
    def goal_speed(self, value):
        self._goal_speed = value

    @property
    def max_accel(self):
        return self._max_accel

    @max_accel.setter
    def max_accel(self, value):
        self._max_accel = value
