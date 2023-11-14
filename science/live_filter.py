import csv
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np


file_name = r"car_data/30.csv"   
positions = []
temps = []
premier_temps = 0

with open(file_name, mode='r', newline='') as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)
        positions = []
        vitesses = []
        temps = []
        for row in reader:
            positions.append(float(row[0]))
            if(len(temps) != 0):
                temps.append(float(row[2]) - premier_temps)
            else:
                temps.append(0)
                premier_temps = float(row[2])
                 

fs = 16.67
fn = fs/2

wp = 2.5/fn
ws = 3.2/fn


ord, wn  = signal.ellipord(wp, ws, 1, 80)
num, denum = signal.ellip(ord, 0.001, 80, wn)


h_w = np.fft.fftshift(np.fft.fft(positions))
h_w = h_w[int(len(h_w)/2):]
plt.plot(np.linspace(0, np.pi, len(h_w)), 20*np.log10((np.abs(h_w))))
plt.xlabel("Fréquence normalisée [rad/éch.]")
plt.ylabel("Amplitude [dB]")
plt.title("Analyse fréquentielle du bruit dans le capteur ultrason")
plt.show()

w, h = signal.freqz(num, denum)

print(ord)


plt.plot(w, 20*np.log10(np.abs(h)))
plt.ylabel("Amplitude [dB]")
plt.xlabel("Fréquence normalisée [rad/éch.]")
plt.title("Réponse en fréquence du filtre passe-bas")
plt.show()


filtered_data = []
z = [0 for _ in range(ord)]

for position in positions:
    data, z = signal.lfilter(num, denum, [position], zi=z)
    filtered_data.append(data[0])


plt.plot(np.linspace(0,int(len(filtered_data)-1), len(filtered_data)), filtered_data)
plt.plot(np.linspace(0,int(len(filtered_data)-1), len(filtered_data)), positions)
plt.legend(["Filtrés", "Brutes"])
plt.ylabel("Position [m]")
plt.xlabel("Éch.")
print(temps)
print(premier_temps)
plt.show()


      
