import bpy
from ir_sensor import Ir_Sensor
from mathutils import Vector

# Utilise cinq sensor pour les cinq capteurs
class LineFollower:
    def __init__(self):
        self.ir1 = Ir_Sensor("CAPTEUR.IR.1")
        self.ir2 = Ir_Sensor("CAPTEUR.IR.2")
        self.ir3 = Ir_Sensor("CAPTEUR.IR.3")
        self.ir4 = Ir_Sensor("CAPTEUR.IR.4")
        self.ir5 = Ir_Sensor("CAPTEUR.IR.5")


    def read_digital(self):
        data = [0, 0, 0, 0, 0]
    
        # Appel la fonction de détection de couleur pour chaque capteur IR
        rgba_u1 = self.ir1.detect_color()
        rgba_u2 = self.ir2.detect_color()
        rgba_u3 = self.ir3.detect_color()
        rgba_u4 = self.ir4.detect_color()
        rgba_u5 = self.ir5.detect_color()
        
        # Tableau de 5 données pour chaque capteur
        data[0] = 1 if rgba_u1 == [0,0,0] else 0
        data[1] = 1 if rgba_u2 == [0,0,0] else 0
        data[2] = 1 if rgba_u3 == [0,0,0] else 0
        data[3] = 1 if rgba_u4 == [0,0,0] else 0
        data[4] = 1 if rgba_u5 == [0,0,0] else 0

        return data