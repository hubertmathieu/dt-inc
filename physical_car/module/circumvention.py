import numpy as np

class Circumvention:
    def __init__(self, wheelbase_m, tire_width_m, default_object_size):
        self._wheelbase_m = wheelbase_m
        self._tirewidth_m = tire_width_m
        self._default_circumvention_distance = default_object_size

    """
    Permet de déterminer les angles de braquage pour effectuer un contournement, en suivant une gaussienne
    """
    def steering_for_circumvention(self, distance_from_object, sampling_time, speed, circumvention_distance=None):
        if circumvention_distance == None:
            circumvention_distance = self._default_circumvention_distance
        rel_position_x = self.define_position_needed(distance_from_object, circumvention_distance, sampling_time, speed)

        distance_travelled = speed*sampling_time
        
        delta_position_x = np.diff(rel_position_x)
        current_angle = np.arcsin(delta_position_x/distance_travelled)
        angle_to_travel_r = np.diff(current_angle)
        angle_to_travel_r = np.concatenate(([0],angle_to_travel_r,[0]))
        

        circle_to_travel_ratio = angle_to_travel_r/(2*np.pi)
        turning_circumference_m = distance_travelled/circle_to_travel_ratio
        turning_radius_m = turning_circumference_m/(2*np.pi)
        stuff_that_goes_inside_arcsin = self._wheelbase_m/(turning_radius_m-self._tirewidth_m/2)
        steering_angle = np.arcsin(stuff_that_goes_inside_arcsin)
        

        end_of_gaussian = int(len(steering_angle)*0.58)
        time_to_go_linear = np.linspace(steering_angle[end_of_gaussian],0, int(1/sampling_time)/3)
        steering_angle = np.concatenate([steering_angle[20:end_of_gaussian], time_to_go_linear])
        return steering_angle


    """
    Défini une fonction gaussienne et retourne les positions X et Y
    """
    def define_position_needed(self, distance_from_object, circumvention_distance, sampling_time, speed):
        overall_distance_travelled_m = distance_from_object * 2
        seconds_travelled = overall_distance_travelled_m / speed

        a = circumvention_distance
        b = distance_from_object
        c = distance_from_object / 5 # constante arbitraire

        # Utilisation d'une gaussienne
        positions_y_m = np.linspace(0,overall_distance_travelled_m, int(seconds_travelled/sampling_time))
        position_x_m = a * np.exp(-(((positions_y_m-b)**2) / ((2*c)**2)))

        return position_x_m

