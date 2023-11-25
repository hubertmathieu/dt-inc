import bpy
import numpy as np
import math

# CONST
FRAME_RATE = bpy.context.scene.render.fps
MAX_ROTATION = math.radians(0.7)
CAR_OBJ = bpy.data.objects["body_high"]
EULER_X = CAR_OBJ.rotation_euler[0]
EULER_Y = CAR_OBJ.rotation_euler[1]
EULER_Z = -CAR_OBJ.rotation_euler[2]

# Global
current_angle = EULER_Z
last_distance = 0

class Front_Wheels():
    def __init__(self):
        self.wheelbase_m = 1.4
        self.tire_width_m = 1.08
        self.frame = 0

    def turn(self, steering_angle, actual_frame):
        self.frame = actual_frame
        self._steering_angle_to_global_angle(steering_angle - (np.pi/2))
        self._set_obj_rotation()

    def _set_obj_rotation(self):
        CAR_OBJ.rotation_euler = [EULER_X, EULER_Y, -current_angle]
        CAR_OBJ.keyframe_insert(data_path="rotation_euler", frame = self.frame + 1)

    def _steering_angle_to_global_angle(self, steering_angle):
        global current_angle

        if(steering_angle != 0):
            turning_radius_m = (self.wheelbase_m / np.sin(np.abs(steering_angle))) + (self.tire_width_m/2)
            turning_circumference_m = 2 * np.pi * turning_radius_m
            circle_traveled_ratio = last_distance / turning_circumference_m
            angle_traveled_r = circle_traveled_ratio*2*np.pi

            if (steering_angle < 0):
                current_angle -= angle_traveled_r
            else:
                current_angle += angle_traveled_r


class Back_Wheels:
    def __init__(self):
        self.max_accel = 0.05 * (1/FRAME_RATE)
        self.current_speed = 0
        self.frame = 0
        self.should_stop = False

    def forward(self, actual_frame):
        self.current_speed = np.abs(self.current_speed)
        self._move(actual_frame)

    def backward(self, actual_frame):
        self.current_speed = -np.abs(self.current_speed)
        self._move(actual_frame)

    def _move(self, actual_frame):
        self.frame = actual_frame
        self._set_next_dist()

    def _set_next_dist(self):
        global last_distance

        # deccelerate
        if (self.should_stop):
            if (self._is_going_backward()):
                next_dist = last_distance + self.max_accel
                if (next_dist >= 0):
                    next_dist = 0
                    self.should_stop = False
            else:
                next_dist = last_distance - self.max_accel
                if (next_dist <= 0):
                    next_dist = 0
                    self.should_stop = False
        #accelerate
        else :
            next_dist = self.current_speed / FRAME_RATE
            # validate if next_dist has too high accel
            if (np.abs(next_dist) > np.abs(last_distance) + self.max_accel):
 
                # adjust next_dist to max_accel
                if (self._is_going_backward()):
                    next_dist = last_distance - self.max_accel
                else:
                    next_dist = last_distance + self.max_accel

        self._set_obj_location(next_dist)
        last_distance = next_dist

    def _set_obj_location(self, next_dist):
        CAR_OBJ.location.x += next_dist * np.sin(current_angle)
        CAR_OBJ.location.y += next_dist * np.cos(current_angle)
        CAR_OBJ.keyframe_insert(data_path="location", frame = self.frame + 1)

    def determine_stopping_dist(self, obstacle_distance):
        if (obstacle_distance > 0 and last_distance != 0 and not self.should_stop):
            dist_to_stop = (last_distance ** 2) / (2*self.max_accel)
            self.should_stop = np.abs(dist_to_stop) > obstacle_distance

    def _is_going_backward(self):
        return self.current_speed < 0

    
    def stopped(self):
        return self.last_distance == 0
    
    @property
    def accel(self):
        return self.max_accel

    @accel.setter
    def accel(self, accel):
        self.max_accel = accel * (1/FRAME_RATE)

    @property
    def speed(self):
        return self.current_speed

    @speed.setter
    def speed(self, speed):
        self.current_speed = speed

    @property
    def last_distance(self):
        return last_distance