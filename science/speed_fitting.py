import csv
import matplotlib.pyplot as plt
import numpy as np

# List of CSV file names
csv_files = ["30.csv", "40.csv", "50.csv", "60.csv", "70.csv", "80.csv","90.csv","100.csv"]
use_case = []

for csv_file_name in csv_files:
    with open(csv_file_name, mode='r', newline='') as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)
        positions = []
        vitesses = []
        temps = []
        for row in reader:
            positions.append(float(row[0]))
            temps.append(float(row[2]))
        use_case.append((positions, temps))
            
fitted = []
slopes = [0]
speed = [0]
current_speed = 30

for case in use_case:
    position_m = np.asarray(case[0])
    time_ns = np.asarray(case[1])
    time_s = np.asarray(time_ns)*1e-9
    coeffs = np.polyfit(time_s, position_m, 1)

    fitted.append((time_s ,time_s*coeffs[0] + coeffs[1]))
    slopes.append(coeffs[0])
    speed.append(current_speed)
    current_speed+=10
    plt.plot(time_s, position_m)

for fit in fitted:
    plt.plot(fit[0], fit[1], "k--")
    
plt.xlabel("Temps [s]")
plt.ylabel("Position [m]")
plt.title("Position en fonction du temps pour plusieurs vitesses")
plt.legend(["30","40","50","60", "70","80", "90","100"])
plt.show()

x_speed = np.linspace(0,100,100)
fitted = np.poly1d((np.polyfit(speed, slopes, 4)))

plt.plot(speed, slopes, "bo")
plt.plot(x_speed, fitted(x_speed))
plt.xlabel("Vitesse des moteurs [%]")
plt.ylabel("Vitesse du véhicule [m/s]")
plt.title("Vitesse du véhicule en fonction des moteurs")
plt.show()



