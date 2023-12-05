import numpy as np

# Constante
XS_MAX_ANGLE = 5
S_MAX_ANGLE = 8
M_MAX_ANGLE = 15
L_MAX_ANGLE = 28
XL_MAX_ANGLE = 45

X_SMALL = 1
SMALL = 2
MEDIUM = 4
LARGE = 6
X_LARGE = 10

max_off_track_count = 10

class Angle_Calculator:
    
    def __init__(self):
        self._ir_status = [0, 0, 0, 0, 0]
        self._max_angle = 0
        self._step = 0
        self._off_track_count = 0
    

    def is_off_track(self):
        """
        Vérifie lorsque la voiture a perdu la ligne depuis un moment

        :return: boolean
        """
        if self._off_track_count >= max_off_track_count:
            return True
        else:
            return False
        
    def reset_off_track_count(self):
        self._off_track_count
        self._ir_status[0] = [[0,0,0,0,0]]
    
    
    def get_steering_angle(self, new_ir_status, steering_angle):
        """
        Utilise le nouveau et le dernier status des capteur pour ajuster l'angle de la direction 

        :new_ir_status: tableau de 5 valeurs (0 ou 1) pour chaque capteur ir
        :steering_angle: angle de la direction en radians
        :return: nouvelle angle de la direction en radians
        """
        print("IR Status:", new_ir_status)
        steering_angle = np.rad2deg(steering_angle)

        if  new_ir_status == [0,0,1,0,0]:
            self._off_track_count = 0
            if steering_angle < -28:
                self._step = LARGE
            elif steering_angle < -15:
                self._step = MEDIUM
            elif steering_angle < -8:
                self._step = SMALL
            elif steering_angle < -5:
                self._step = X_SMALL
            elif steering_angle > 28:
                self._step = -LARGE
            elif steering_angle > 15:
                self._step = -MEDIUM
            elif steering_angle > 8:
                self._step = -SMALL
            elif steering_angle > 5:
                self._step = -X_SMALL
        elif new_ir_status == [0,1,1,0,0]:
            self._off_track_count = 0
            self._max_angle = XS_MAX_ANGLE
            self._step = X_SMALL
        elif new_ir_status == [0,1,0,0,0]:
            self._off_track_count = 0
            self._max_angle = S_MAX_ANGLE
            self._step = SMALL
        elif new_ir_status == [1,1,0,0,0]:
            self._off_track_count = 0
            self._max_angle = M_MAX_ANGLE
            self._step = MEDIUM
        elif new_ir_status == [1,0,0,0,0]:
            self._off_track_count = 0
            self._max_angle = L_MAX_ANGLE
            self._step = LARGE
        elif new_ir_status == [0,0,1,1,0]:
            self._off_track_count = 0
            self._max_angle = -XS_MAX_ANGLE
            self._step = -X_SMALL
        elif new_ir_status == [0,0,0,1,0]:
            self._off_track_count = 0
            self._max_angle = -S_MAX_ANGLE
            self._step = -SMALL
        elif new_ir_status == [0,0,0,1,1]:
            self._off_track_count = 0
            self._max_angle = -M_MAX_ANGLE
            self._step = -MEDIUM
        elif new_ir_status == [0,0,0,0,1]:
            self._off_track_count = 0
            self._max_angle = -L_MAX_ANGLE
            self._step = -LARGE
        elif new_ir_status == [0,0,0,0,0]:
            self._off_track_count += 1
            if self._ir_status[0] == 1:
                self._max_angle = XL_MAX_ANGLE
                self._step = X_LARGE
            elif self._ir_status[4] == 1:
                self._max_angle = -XL_MAX_ANGLE
                self._step = -X_LARGE
            else:
                print("Steering angle dans le return:", steering_angle)
                return np.deg2rad(steering_angle)
            
        steering_angle += self._step
            
        if steering_angle < self._max_angle:
            steering_angle = self._max_angle
        elif steering_angle > self._max_angle:
            steering_angle = self._max_angle
        
        self._ir_status = new_ir_status
        print("Steering angle:", steering_angle)
        return np.deg2rad(steering_angle)