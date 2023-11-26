import numpy as np

wheelbase_m = 1.4
tire_width_m = 1.08


def define_position_needed_to_contourne_object(distance_avant_objet, distance_objet_apres, distance_qu_on_contourne_m,
                                               sampling_time, vitesse):
    # using a gaussian to define a relative x,y position function
    overall_distance_travelled_m = distance_avant_objet + distance_objet_apres
    seconds_travelled = overall_distance_travelled_m / vitesse

    a = distance_qu_on_contourne_m
    b = distance_avant_objet
    c = distance_avant_objet / 5

    positions_y_m = np.linspace(0, overall_distance_travelled_m, int(seconds_travelled / sampling_time))
    position_x_m = a * np.exp(-(((positions_y_m - b) ** 2) / ((2 * c) ** 2)))
    return position_x_m, positions_y_m


def donne_moi_le_steering_pour_faire_le_contournement(distance_de_objet_avant=6, distance_de_objet_cote=-1.8,
                                                      sampling_time=(1 / 24), vitesse=1.5):
    relative_position_x, _ = define_position_needed_to_contourne_object(distance_de_objet_avant,
                                                                        distance_de_objet_avant, distance_de_objet_cote,
                                                                        sampling_time, vitesse)

    distance_travelled = vitesse * sampling_time
    delta_position_x = np.diff(relative_position_x)

    current_angle = -np.arcsin(delta_position_x / distance_travelled)

    angle_to_travel_r = np.diff(current_angle)

    angle_to_travel_r = np.concatenate(([0], angle_to_travel_r, [0]))

    circle_to_travel_ratio = angle_to_travel_r / (2 * np.pi)
    turning_circumference_m = (distance_travelled) / circle_to_travel_ratio
    turning_radius_m = turning_circumference_m / (2 * np.pi)
    stuff_that_goes_inside_arcsin = wheelbase_m / (turning_radius_m - tire_width_m / 2)
    steering_angle = np.arcsin(stuff_that_goes_inside_arcsin)

    trois_quart = int(len(steering_angle) * 0.5)
    error = np.cumsum(steering_angle)[-1]
    minimum = np.min(steering_angle)
    tricherie = [minimum for _ in range(int(error / (np.abs(minimum)) + 4))]
    steering_angle = np.concatenate([steering_angle[:trois_quart], tricherie, steering_angle[trois_quart:]])

    return steering_angle


def main():
    import matplotlib.pyplot as plt
    steering = donne_moi_le_steering_pour_faire_le_contournement()
    plt.plot(np.linspace(0, len(steering) - 1, len(steering)), steering)
    plt.plot(np.linspace(0, len(steering) - 1, len(steering)), np.cumsum(steering))
    plt.show()
    print(len(steering))


if __name__ == "__main__":
    main()
