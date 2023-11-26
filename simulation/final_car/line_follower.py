import bpy
from ir_sensor import Sensor
from mathutils import Vector

# Utilise cinq sensor pour les cinq capteurs
class LineFollower:
    def __init__(self):
        self.u1 = Sensor("CAPTEUR.IR.1")
        self.u2 = Sensor("CAPTEUR.IR.2")
        self.u3 = Sensor("CAPTEUR.IR.3")
        self.u4 = Sensor("CAPTEUR.IR.4")
        self.u5 = Sensor("CAPTEUR.IR.5")


    def read_digital(self):
        data = [0, 0, 0, 0, 0]
    
        # Detect color for every sensors
        rgba_u1 = self.u1.detect_color()
        rgba_u2 = self.u2.detect_color()
        rgba_u3 = self.u3.detect_color()
        rgba_u4 = self.u4.detect_color()
        rgba_u5 = self.u5.detect_color()
        
        # Creates an array of digital data if black color is detected
        data[0] = 1 if rgba_u1 == [0,0,0] else 0
        data[1] = 1 if rgba_u2 == [0,0,0] else 0
        data[2] = 1 if rgba_u3 == [0,0,0] else 0
        data[3] = 1 if rgba_u4 == [0,0,0] else 0
        data[4] = 1 if rgba_u5 == [0,0,0] else 0

        return data