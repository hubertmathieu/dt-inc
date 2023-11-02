import numpy as np
import matplotlib.pyplot as plt

t = np.linspace(0,10,100)

def speed_position_for_constant_acceleration(acceleration, t, v0=0, p0=0):
    speed = t*acceleration+v0
    position = (t**2)*(acceleration/2)+p0
    return speed, position

def find_position_for_deceleration( v0, max_decel):
    return -v0**2/2*max_decel
    
    
acceleration = 0.2
speed, position = speed_position_for_constant_acceleration(acceleration, t)
plt.plot(t, [acceleration for _ in range(len(t))], "b-")
plt.plot(t, speed, "r-")
plt.plot(t, position, "g-")
plt.legend(["Acceleration [m/s^2]", "Speed [m/s]", "Position [m]"])
plt.title("Vitesse et position en fonction d'une accélération constante")
plt.show()


acceleration = -0.2
speed, position = speed_position_for_constant_acceleration(acceleration, t)
plt.plot(t, [acceleration for _ in range(len(t))], "b-")
plt.plot(t, speed, "r-")
plt.plot(t, position, "g-")
plt.legend(["Acceleration [m/s^2]", "Speed [m/s]", "Position [m]"])
plt.title("Vitesse et position en fonction d'une décélération constante")
plt.show()

print (find_position_for_deceleration(2, 0.2))


