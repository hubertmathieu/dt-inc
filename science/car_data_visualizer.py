from car.car import CarMeasurement
import csv
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter



csv_file = r"car_data/3m_02.csv"
csv_file = r"car_data/3m_02.csv"
csv_file = r"car_data/circle.csv"

measurements = []


with open(csv_file, mode='r', newline='') as csv_file:
    reader = csv.reader(csv_file)
    next(reader, None)
        
    for row in reader:
        measurement = CarMeasurement(float(row[0]),float(row[1]),float(row[2]),float(row[3]),float(row[4]),float(row[5]),float(row[6]))
        measurements.append(measurement)

position_x = [measurement.position_x for measurement in measurements]
position_y = [measurement.position_y for measurement in measurements]

position_x = position_x[::25]
position_y = position_y[::25]


plt.scatter(position_x, position_y)
plt.ylabel("Y [m]")
plt.xlabel("X [m]")
plt.title("Position du véhicule dans l'espace")
ax = plt.gca()
ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
plt.xticks(range(-1,1))
plt.show()
            