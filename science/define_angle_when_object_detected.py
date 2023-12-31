import numpy as np
import matplotlib.pyplot as plt

wheelbase_m = 0.14
tire_width_m = 0.108

def define_position_needed_to_contourne_object(distance_avant_objet,distance_objet_apres, distance_qu_on_contourne_m, sampling_time, vitesse):
    # using a gaussian to define a relative x,y position function
    overall_distance_travelled_m = distance_avant_objet+distance_objet_apres
    seconds_travelled = overall_distance_travelled_m/vitesse

    a = distance_qu_on_contourne_m
    b = distance_avant_objet
    c = distance_avant_objet / 5

    positions_y_m = np.linspace(0,overall_distance_travelled_m, int(seconds_travelled/sampling_time))
    position_x_m = a * np.exp(-(((positions_y_m-b)**2) / ((2*c)**2)))
    return position_x_m, positions_y_m

def donne_moi_le_steering_pour_faire_le_contournement():
    distance_avant_objet = 0.7
    distance_apres_objet = 0.7
    distance_qu_on_veut_etre_loin_de_l_object = -0.25
    sampling_time = 1/60
    vitesse = 0.15
    relative_position_x, relative_position_y = define_position_needed_to_contourne_object(distance_avant_objet, distance_apres_objet, distance_qu_on_veut_etre_loin_de_l_object, sampling_time, vitesse)

    distance_travelled = vitesse*sampling_time
    delta_position_x = np.diff(relative_position_x)

    current_angle = -np.arcsin(delta_position_x/distance_travelled)
    
    angle_to_travel_r = np.diff(current_angle)

    angle_to_travel_r = np.concatenate(([0],angle_to_travel_r,[0]))

    circle_to_travel_ratio = angle_to_travel_r/(2*np.pi)
    turning_circumference_m = (distance_travelled)/circle_to_travel_ratio
    turning_radius_m = turning_circumference_m/(2*np.pi)
    stuff_that_goes_inside_arcsin = wheelbase_m/(turning_radius_m-tire_width_m/2)
    steering_angle = np.arcsin(stuff_that_goes_inside_arcsin)

    trois_quart = int(len(steering_angle)*0.5)
    error = np.cumsum(steering_angle)[-1]
    minimum = np.min(steering_angle)
    print(minimum)
    tricherie = [minimum for _ in range (int(error/(np.abs(minimum))))]
    steering_angle = np.concatenate([steering_angle[:trois_quart], tricherie, steering_angle[trois_quart:]])

    
    

    plt.plot(relative_position_x, relative_position_y)
    plt.axvline(0, color="green", linestyle="--")
    plt.plot(0, distance_avant_objet, "ro")
    plt.xticks(range(-3,4))
    plt.xlabel("X [m]")
    plt.ylabel("Y [m]")
    plt.title("Fonction de position du véhicule pour un déplacement à vitesse fixe")
    plt.legend(["Fonction de position", "Ligne guide", "Objet à contourner"])
    plt.show() 
#
    plt.plot(relative_position_y[:-1], current_angle)
    plt.plot(relative_position_y, angle_to_travel_r)
    plt.ylabel("Angle [rad]")
    plt.xlabel("Y [m]")
    plt.title("Angle du véhicule en fonction de la position")
    plt.show()
#
    plt.plot(relative_position_y,circle_to_travel_ratio)
    plt.plot(relative_position_y,turning_circumference_m)
    plt.plot(relative_position_y,turning_radius_m)
    plt.show()
#
    plt.plot(np.linspace(0,len(steering_angle)-1, len(steering_angle)), steering_angle)
    plt.plot(np.linspace(0,len(steering_angle)-1, len(steering_angle)), np.cumsum(steering_angle))
    plt.title("Angle de braquage en fonction de la position")
    plt.ylabel("Angle [rad]")
    plt.xlabel("Y [m]")
    plt.show()

    return steering_angle

    
def main():
    steering = donne_moi_le_steering_pour_faire_le_contournement()






    

if __name__ == "__main__":
    main()
