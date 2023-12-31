import numpy as np
import matplotlib.pyplot as plt

seconds_elapsed = 0.06

position_x = 0
position_y = 0

all_position_x = [0]
all_position_y = [0]

current_angle = np.pi/2

wheelbase_m = 0.14
tire_width_m = 0.108

def calculate_position(speed, steering_angle):
    global position_x
    global position_y
    global current_angle

    if(steering_angle != 0):
        turning_radius_m = (wheelbase_m / np.sin(np.abs(steering_angle))) + (tire_width_m/2)
        turning_circumference_m = 2 * np.pi * turning_radius_m
        circle_traveled_ratio = (speed*seconds_elapsed) / turning_circumference_m
        angle_traveled_r = circle_traveled_ratio*2*np.pi

        if(angle_traveled_r < 0):
            current_angle = current_angle-angle_traveled_r
        else:
            current_angle = current_angle+angle_traveled_r

        distance_traveled = speed*seconds_elapsed
        delta_position_x=np.cos(current_angle)*distance_traveled
        delta_position_y=np.sin(current_angle)*distance_traveled
        position_x+=delta_position_x
        position_y+=delta_position_y
        all_position_x.append(position_x)
        all_position_y.append(position_y)
    else:
        distance_traveled = speed*seconds_elapsed
        delta_position_x=np.cos(current_angle)*distance_traveled
        delta_position_y=np.sin(current_angle)*distance_traveled
        position_x+=delta_position_x
        position_y+=delta_position_y
        all_position_x.append(position_x)
        all_position_y.append(position_y)
        

## TESTING
vitesse = 0.15 # m/s
turning_angle_d = np.concatenate((np.linspace(0, 30, 100),np.linspace(30, 0, 50), np.linspace(30, 0, 50), np.zeros(200), np.linspace(0, -15, 100), np.linspace(-15, -15, 100), np.linspace(-15, 0, 100), np.zeros(500)))
turning_angle_r = (turning_angle_d/360)*(2*np.pi)
    
for turning_angle in turning_angle_r:
    calculate_position(vitesse, turning_angle)

plt.scatter(all_position_x, all_position_y)
plt.title("Suivi de la position du véhicule")
plt.xlabel("X [m]")
plt.ylabel("Y [m]")
plt.grid()
plt.show()
