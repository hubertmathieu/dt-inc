import bpy
import sys
import math

EULER_X = math.radians(-90)
EULER_Y = math.radians(0)
EULER_Z = math.radians(-90)

# Make python file in the main directory accessible for imports
blend_file_directory = bpy.path.abspath('//')
sys.path.append(blend_file_directory)

# obj name
car_name = "body_high"

# Imports all the neccessary python file
from line_follower import LineFollower
from car_simul import Back_Wheels
from car_simul import Front_Wheels
from ultrasonic_avoidance import Ultrasonic_Avoidance

lf = LineFollower()
fw = Front_Wheels()
bw = Back_Wheels()
ua_1 = Ultrasonic_Avoidance(car_name)

frame = 0
turning_angle = 90
a_step = 3
b_step = 10
c_step = 30
d_step = 45

def init_objects():
    # init car position
    obj = bpy.data.objects[car_name]
    obj.animation_data_clear()
    obj.location = (22.8,2.5,2)
    obj.rotation_euler = [EULER_X, EULER_Y, -EULER_Z]
    obj.keyframe_insert(data_path="rotation_euler", frame = 0)
    obj = bpy.data.objects[car_name]


def follow_line(frame):
    global turning_angle
    
    lt_status_now = lf.read_digital()
    #print(lt_status_now)
    # Angle calculate
    if	lt_status_now == [0,0,1,0,0]:
        step = 0	
    elif lt_status_now == [0,1,1,0,0] or lt_status_now == [0,0,1,1,0]:
        step = a_step
    elif lt_status_now == [0,1,0,0,0] or lt_status_now == [0,0,0,1,0]:
        step = b_step
    elif lt_status_now == [1,1,0,0,0] or lt_status_now == [0,0,0,1,1]:
        step = c_step
    elif lt_status_now == [1,0,0,0,0] or lt_status_now == [0,0,0,0,1]:
        step = d_step
    elif lt_status_now == [0,0,0,0,0]:
        step = d_step

    # Direction calculate
    if	lt_status_now == [0,0,1,0,0]:
        turning_angle = 90
    # turn right
    elif lt_status_now in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0],[1,0,0,0,0]):
        turning_angle = int(90 - step)
    # turn left
    elif lt_status_now in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1],[0,0,0,0,1]):
        turning_angle = int(90 + step)
    #find line
    elif lt_status_now == [0,0,0,0,0]:
        if turning_angle > 90:
            turning_angle = int(90 + step)
        elif turning_angle < 90:
            turning_angle = int(90 - step)
    else:
        turning_angle = 90

    fw.turn(math.radians(turning_angle), frame)

def detect_object():
    ua_1_distance = ua_1.get_distance()

    #print(ua_1_distance)

    if ua_1_distance != -1:
        bw.determine_stopping_dist(ua_1_distance)

def move_back():
    global frame
    stopping_distance = 3

    while(frame < 2000):
        bw.backward(frame)
        stopping_distance += bw.last_distance
        bw.determine_stopping_dist(stopping_distance)
        if (bw.stopped()):
            break
        frame += 1

def main():
    global frame
    bw.speed = 1.5

    while(frame < 2000):
        bw.forward(frame)
        follow_line(frame)
        detect_object()

        if (bw.stopped()):
            frame += 15
            move_back()

        frame += 1


if __name__ == '__main__':
    init_objects()
    main()

