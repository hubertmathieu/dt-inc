from SunFounder_PiCar_S.example.SunFounder_Ultrasonic_Avoidance import Ultrasonic_Avoidance
from SunFounder_PiCar.picar.back_wheels import Back_Wheels
from SunFounder_PiCar.picar.front_wheels import Front_Wheels

from time import sleep
import time
from datetime import datetime
import csv
import math
Ts = 0.2 # 60 ms env
starting_position = 3 # m
speed = 50
angle = math.pi/4

distances = []
vitesses = []
times = []

timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
csv_file_name = f"output_{timestamp}.csv"


if __name__ == "__main__":
    back_wheels = Back_Wheels()
    front_wheels = Front_Wheels()
    UA = Ultrasonic_Avoidance.Ultrasonic_Avoidance(20)
    back_wheels.backward()
    back_wheels.speed = speed
    starting_time = time.time_ns()
    front_wheels.turn(angle*(180/math.pi))
    d_m = 3
    
    while d_m > 0.1:
        d = UA.get_distance()
        if d != -1:
            d_m = d*0.01
        print(d)
        current_position = starting_position - d_m
        distances.append(current_position)
        back_wheels.speed = speed
        vitesses.append(speed)
        current_time = time.time_ns()
        times.append(current_time - starting_time)
        sleep(Ts)
    back_wheels.speed = 0
    with open(csv_file_name, mode="w", newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["position", "vitesse", "temps"])
        for i in range(len(distances)):
            writer.writerow([distances[i],vitesses[i],times[i]])