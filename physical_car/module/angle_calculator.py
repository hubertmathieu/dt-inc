import numpy as np

# Constante
X_SMALL = 0.1
SMALL = 0.25
MEDIUM = 0.5
LARGE = 0.75
X_LARGE = 1.25

max_off_track_count = 40

class Angle_Calculator:
    
    def __init__(self):
        self._ir_status = [0, 0, 0, 0, 0]
        self._step = 0
        self._off_track_count = 0
    

    def is_off_track(self):
        """
        Vérifie lorsque la voiture a perdu la ligne depuis un moment

        :return: boolean
        """
        if self._off_track_count >= max_off_track_count:
            self._off_track_count = 0
            return True
        else:
            return False
    
    
    def get_steering_angle(self, new_ir_status, steering_angle):
        """
        Utilise le nouveau et le dernier status des capteur pour ajuster l'angle de la direction 

        :new_ir_status: tableau de 5 valeurs (0 ou 1) pour chaque capteur ir
        :steering_angle: angle de la direction en radians
        :return: nouvelle angle de la direction en radians
        """
        print("IR Status:", new_ir_status)
        steering_angle = np.rad2deg(steering_angle)

        if	new_ir_status == [0,0,1,0,0]:
            if steering_angle < -30:
                self._step = LARGE
            elif steering_angle < -15:
                self._step = MEDIUM
            elif steering_angle < -5:
                self._step = SMALL
            elif steering_angle < -3:
                self._step = X_SMALL
            elif steering_angle > 30:
                self._step = -LARGE
            elif steering_angle > 15:
                self._step = -MEDIUM
            elif steering_angle > 5:
                self._step = -SMALL
            elif steering_angle > 3:
                self._step = -X_SMALL
        elif new_ir_status == [0,1,1,0,0]:
            self._step = X_SMALL
        elif new_ir_status == [0,1,0,0,0]:
            self._step = SMALL
        elif new_ir_status == [1,1,0,0,0]:
            self._step = MEDIUM
        elif new_ir_status == [1,0,0,0,0]:
            self._step = LARGE
        elif new_ir_status == [0,0,1,1,0]:
            self._step = -X_SMALL
        elif new_ir_status == [0,0,0,1,0]:
            self._step = -SMALL
        elif new_ir_status == [0,0,0,1,1]:
            self._step = -MEDIUM
        elif new_ir_status == [0,0,0,0,1]:
            self._step = -LARGE
        elif new_ir_status == [0,0,0,0,0]:
            self._off_track_count += 1
            if self._ir_status[0] == 1:
                self._step = X_LARGE
            elif self._ir_status[4] == 1:
                self._step = -X_LARGE
            
        steering_angle += self._step
            
        if steering_angle < -45:
            steering_angle = -45
        elif steering_angle > 45:
            steering_angle = 45
        elif steering_angle < 1 and steering_angle > -1:
            steering_angle = 0
        
        self._ir_status = new_ir_status
        print("Steering angle:", steering_angle)
        return np.deg2rad(steering_angle)