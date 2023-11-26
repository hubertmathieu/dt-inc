import numpy as np
 
X_SMALL = 0.1
SMALL = 0.25
MEDIUM = 0.5
LARGE = 0.75
X_LARGE = 1.25

class Angle_Calculator:
    
    def __init__(self):
        self._ir_status = [0, 0, 0, 0, 0]
        self._step = 0
    
    def get_steering_angle(self, new_ir_status, steering_angle):
        """
        Check the status of the ir sensor and calculate the new steering angle for the car 

        :new_ir_status: array of 5 value that represent each ir sensor
        :steering_angle: steering angle of the car at that moment (in radian)
        :return: steering_angle for the car to turn
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