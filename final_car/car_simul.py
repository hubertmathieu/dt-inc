import bpy
import numpy as np
import math

# CONST
FRAME_RATE = bpy.context.scene.render.fps
EULER_X = math.radians(-90)
EULER_Y = math.radians(0)
EULER_Z = math.radians(-90)
MAX_ACCEL = 0.1 * (1/FRAME_RATE)
CAR_OBJ = bpy.data.objects["body_high"]

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
        CAR_OBJ.rotation_euler = [EULER_X, EULER_Y, -current_angle ]
        CAR_OBJ.keyframe_insert(data_path="rotation_euler", frame = self.frame + 1)

    def _adjust_rotation(self, final_angle):
        # if (np.abs(final_angle - current_angle) >= 2):
        #     return 2
        # else :
            return final_angle

    def _steering_angle_to_global_angle(self, steering_angle):
        global current_angle

        if(steering_angle != 0):
            turning_radius_m = (self.wheelbase_m / np.sin(np.abs(steering_angle))) + (self.tire_width_m/2)
            turning_circumference_m = 2 * np.pi * turning_radius_m
            circle_traveled_ratio = last_distance / turning_circumference_m
            angle_traveled_r = circle_traveled_ratio*2*np.pi

            next_angle_variation = self._adjust_rotation(angle_traveled_r)

            if (steering_angle < 0):
                current_angle -= next_angle_variation
            else:
                current_angle += next_angle_variation


class Back_Wheels:
    def __init__(self):
        self.current_speed = 0
        self.frame = 0
        self.should_stop = False

    def forward(self, actual_frame):
        self.current_speed = np.abs(self.current_speed)
        self._move(actual_frame)

    def backward(self, actual_frame):
        self.current_speed = -self.current_speed
        self._move(actual_frame)

    def _move(self, actual_frame):
        self.frame = actual_frame
        self._set_next_dist()

    def _set_next_dist(self):
        global last_distance

        # deccelerate
        if (self.should_stop):
            next_dist = last_distance - MAX_ACCEL
            next_dist = 0 if (next_dist <= 0) else next_dist 
        #accelerate
        else :
            next_dist = self.current_speed / FRAME_RATE
            if (next_dist > last_distance + MAX_ACCEL):
                next_dist = last_distance + MAX_ACCEL

        self._set_obj_location(next_dist)

        last_distance = next_dist

    def _set_obj_location(self, next_dist):
        CAR_OBJ.location.x += next_dist * np.sin(current_angle)
        CAR_OBJ.location.y += next_dist * np.cos(current_angle)
        CAR_OBJ.keyframe_insert(data_path="location", frame = self.frame + 1)

    def determine_stopping_dist(self, obstacle_distance):
        print("last dist : ", last_distance)
        print("obstacle_distance : ", obstacle_distance)
        print("stop : ", self.should_stop)
        if (obstacle_distance > 0 and last_distance > 0 and not self.should_stop):
                dist_to_stop = (last_distance ** 2) / (2*MAX_ACCEL)
                print("dist_to_stop : ", dist_to_stop)

                self.should_stop = dist_to_stop > obstacle_distance

    @property
    def speed(self):
        return self.current_speed

    @speed.setter
    def speed(self, speed):
        self.current_speed = speed

    @property
    def last_distance(self):
        return last_distance