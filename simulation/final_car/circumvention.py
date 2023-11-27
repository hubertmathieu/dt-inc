import numpy as np


class Circumvention():

    def __init__(self):
        self._wheelbase_m = 1.4
        self.tire_width_m = 1.08

    """
    Défini une fonction gaussienne et retourne les positions X et Y
    """
    def _define_position_for_circumvention(self, distance_avant_objet, distance_objet_apres, distance_qu_on_contourne_m,
                                                sampling_time, vitesse):
        # Utilise une gausienne pour définir les positions x et y relatives du véhicule
        overall_distance_travelled_m = distance_avant_objet + distance_objet_apres
        seconds_travelled = overall_distance_travelled_m / vitesse

        a = distance_qu_on_contourne_m
        b = distance_avant_objet
        c = distance_avant_objet / 5 # ce coefficient est heuristique

        # position en Y (linéaire)
        positions_y_m = np.linspace(0, overall_distance_travelled_m, int(seconds_travelled / sampling_time))
        # position en X (gaussienne)
        position_x_m = a * np.exp(-(((positions_y_m - b) ** 2) / ((2 * c) ** 2)))
        return position_x_m, positions_y_m

    """
    Permet de déterminer les angles de braquage pour effectuer un contournement, en suivant une gaussienne
    """
    def steering_for_circumvention(self, distance_de_objet_avant=6, distance_de_objet_cote=-1.8, sampling_time=(1 / 24), vitesse=1.5):
        relative_position_x, _ = self._define_position_for_circumvention(distance_de_objet_avant,
                                                                    distance_de_objet_avant,
                                                                    distance_de_objet_cote,
                                                                    sampling_time, vitesse)

        distance_travelled = vitesse * sampling_time

        delta_position_x = np.diff(relative_position_x)

        current_angle = -np.arcsin(delta_position_x / distance_travelled)

        angle_to_travel_r = np.diff(current_angle)

        angle_to_travel_r = np.concatenate(([0], angle_to_travel_r, [0]))

        circle_to_travel_ratio = angle_to_travel_r / (2 * np.pi)
        turning_circumference_m = (distance_travelled) / circle_to_travel_ratio
        turning_radius_m = turning_circumference_m / (2 * np.pi)
        stuff_that_goes_inside_arcsin = self._wheelbase_m / (turning_radius_m - self.tire_width_m / 2)
        steering_angle = np.arcsin(stuff_that_goes_inside_arcsin)

        trois_quart = int(len(steering_angle) * 0.5)

        error = np.cumsum(steering_angle)[-1]

        minimum = np.min(steering_angle)
        
        # Petit fix pour s'assurer de respecter l'angle totale de 0 degrée
        tricherie = [minimum for _ in range(int(error / (np.abs(minimum)) + 4))]

        steering_angle = np.concatenate([steering_angle[:trois_quart], tricherie, steering_angle[trois_quart:]])

        return steering_angle


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    steering = Circumvention().steering_for_circumvention()
    plt.plot(np.linspace(0, len(steering) - 1, len(steering)), steering)
    plt.plot(np.linspace(0, len(steering) - 1, len(steering)), np.cumsum(steering))
    plt.show()
    print(len(steering))
