import csv
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
from collections import deque


file_name = "30.csv"   
positions = []
temps = []

with open(file_name, mode='r', newline='') as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)
        positions = []
        vitesses = []
        temps = []
        for row in reader:
            positions.append(float(row[0]))
            temps.append(float(row[2]))

fs = 16.67
fn = fs/2

wp = 2.5/fn
ws = 3.2/fn

ord, wn  = signal.ellipord(wp, ws, 1, 80)
num, denum = signal.ellip(ord, 0.001, 80, wn)

w, h = signal.freqz(num, denum)

print(ord)
plt.plot(w, 20*np.log10(np.abs(h)))
plt.show()


filtered_data = []
z = [0 for _ in range(ord)]

for position in positions:
    data, z = signal.lfilter(num, denum, [position], zi=z)
    filtered_data.append(data[0])


plt.plot(temps, filtered_data)
plt.plot(temps, positions)
# plt.plot(temps, signal.lfilter(num, denum, positions))
plt.legend(["Stream filtered", "Raw positions", "Full filtered"])
plt.show()


      
