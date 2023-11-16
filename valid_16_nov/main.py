import bpy
import sys
import math


# Make python file in the main directory accessible for imports
blend_file_directory = bpy.path.abspath('//')
sys.path.append(blend_file_directory)

# Imports all the neccessary python file
from line_follower import LineFollower
from car_simul import Back_Wheels
from car_simul import Front_Wheels
from ultrasonic_avoidance import Ultrasonic_Avoidance
from define_angle_when_object_detecteddd import donne_moi_le_steering_pour_faire_le_contournement

# CONSTANTE
CAR_NAME = "body_high"
EULER_X = math.radians(-90)
EULER_Y = math.radians(0)
EULER_Z = math.radians(-90)

# Class object from other file
lf = LineFollower()
fw = Front_Wheels()
bw = Back_Wheels()
ua_1 = Ultrasonic_Avoidance(CAR_NAME)

frame = 0
turning_angle = 90

class CarController:
    def follow_line(self):
        global frame
        global turning_angle
        
        lt_status_now = lf.read_digital()
        print("frame:", frame, "status:", lt_status_now)
        # Angle calculate
        if	lt_status_now == [0,0,1,0,0]:
            step = 0	
        elif lt_status_now == [0,1,1,0,0] or lt_status_now == [0,0,1,1,0]:
            step = 0.3
        elif lt_status_now == [0,1,0,0,0] or lt_status_now == [0,0,0,1,0]:
            step = 0.5
        elif lt_status_now == [1,1,0,0,0] or lt_status_now == [0,0,0,1,1]:
            step = 0.7
        elif lt_status_now == [1,0,0,0,0] or lt_status_now == [0,0,0,0,1]:
            step = 1
        elif lt_status_now == [0,0,0,0,0]:
            step = 1
        elif lt_status_now == [1,1,1,1,1]:
            self.stop()
            return

        # Direction calculate
        if	lt_status_now == [0,0,1,0,0]:
            turning_angle = 90
        # turn right
        elif lt_status_now in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0],[1,0,0,0,0]):
            turning_angle -= step
        # turn left
        elif lt_status_now in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1],[0,0,0,0,1]):
            turning_angle += step
        #find line
        elif lt_status_now == [0,0,0,0,0]:
            if turning_angle > 90:
                turning_angle += step
            elif turning_angle < 90:
                turning_angle -= step

        fw.turn(math.radians(turning_angle), frame)

    def stop(self):
        self.move_at_distance(1, bw.speed > 0)

    def move_at_distance(self ,stopping_distance, forward=True):
        global frame
        while(1):
            if (forward):
                bw.forward(frame)
                stopping_distance -= bw.last_distance
            else:
                bw.backward(frame)
                stopping_distance += bw.last_distance

            bw.determine_stopping_dist(stopping_distance)
            if (bw.stopped()):
                frame += 15
                break

            frame += 1

    def detect_object_and_stop(self):
        ua_1_distance = ua_1.get_distance()

        if ua_1_distance != -1:
            bw.determine_stopping_dist(ua_1_distance)

    def get_around_obstacle(self):
        global frame
        steering_angles = donne_moi_le_steering_pour_faire_le_contournement()

        for caliss_dangle in steering_angles:
            bw.forward(frame)
            fw.turn(caliss_dangle + (math.pi/2), frame)
            frame+= 1



car_controller = CarController()

def init_objects(pos, rot):
    # init car position
    obj = bpy.data.objects[CAR_NAME]
    obj.animation_data_clear()
    obj.location = pos
    obj.rotation_euler = rot
    obj.keyframe_insert(data_path="rotation_euler", frame = 0)
    obj = bpy.data.objects[CAR_NAME]


def parcours1_widecurve():
    global frame
    init_objects((18,-1.9,0.75), [EULER_X, EULER_Y, -EULER_Z])
    frame = 15
    bw.speed = 3

    while(frame < 2000):
        bw.forward(frame)
        car_controller.follow_line()
        frame += 1

def parcours2_stop():
    global frame
    init_objects((-11,0,0.75), [EULER_X, EULER_Y, -EULER_Z])
    frame = 15
    bw.speed = 2

    while(frame < 2000):
        if(bw.speed == 0):
            break
        bw.forward(frame)
        car_controller.follow_line()
        frame += 1

def parcours3_moveback():
    global frame
    init_objects((0,0,0.75), [EULER_X, EULER_Y, -EULER_Z])
    frame = 15
    bw.speed = 2.5
    
    car_controller.move_at_distance(3, False)

def parcours4_obstacle():
    global frame
    init_objects((7.9,0,0.75), [EULER_X, EULER_Y, -EULER_Z])
    frame = 15
    bw.speed = 1.5

    while(frame < 2000):
        bw.forward(frame)
        car_controller.follow_line()
        car_controller.detect_object_and_stop()

        if (bw.stopped()):
            frame += 15
            car_controller.move_at_distance(3, False)
            car_controller.get_around_obstacle()
        frame += 1

if __name__ == '__main__':
    #parcours1_widecurve()
    #parcours2_stop()
    #parcours3_moveback()
    parcours4_obstacle()

