import bpy
import sys
import math


# Permet à blender de détecter l'importation de fichgier externe en ajustant le path
blend_file_directory = bpy.path.abspath('//')
sys.path.append(blend_file_directory)

# Importer les classes importantes
from line_follower import LineFollower
from car_simul import Back_Wheels
from car_simul import Front_Wheels
from ultrasonic_avoidance import Ultrasonic_Avoidance
from circumvention import Circumvention

# CONSTANTE
CAR_NAME = "body_high"
EULER_X = math.radians(-90)
EULER_Y = math.radians(0)
EULER_Z = math.radians(-90)

# Objet de classe venant de fichier externe
lf = LineFollower()
fw = Front_Wheels()
bw = Back_Wheels()
ua_1 = Ultrasonic_Avoidance(CAR_NAME)
circ = Circumvention()

frame = 0
turning_angle = 90

# Définit les actions du véhicule en fonction des capteurs
class CarController:
    # suiveur de ligne
    def follow_line(self):
        global frame
        global turning_angle
        
        lt_status_now = lf.read_digital()
        print("frame:", frame, "status:", lt_status_now, "turning angle:", turning_angle)
        # Calculer l'angle selon le status
        if	lt_status_now == [0,0,1,0,0]:
            step = 0
        elif lt_status_now == [0,1,1,0,0] or lt_status_now == [0,0,1,1,0]:
            step = 2
        elif lt_status_now == [0,1,0,0,0] or lt_status_now == [0,0,0,1,0]:
            step = 7
        elif lt_status_now == [1,1,0,0,0] or lt_status_now == [0,0,0,1,1]:
            step = 10
        elif lt_status_now == [1,0,0,0,0] or lt_status_now == [0,0,0,0,1]:
            step = 13
        elif lt_status_now == [1,1,1,1,1]:
            self.stop()
            return

        # Calcule de direction (gauche ou droit)
        if	lt_status_now == [0,0,1,0,0]:
            if turning_angle < 90:
                turning_angle += 1
            elif turning_angle > 90:
                turning_angle -= 1
            else:
                turning_angle = 90
        # tourne vers la droite
        elif lt_status_now in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0],[1,0,0,0,0]):
            if turning_angle > 0:
                turning_angle -= step
            else:
                turning_angle = 0
        # tourne vers la gauche
        elif lt_status_now in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1],[0,0,0,0,1]):
            if turning_angle < 135:
                turning_angle += step
            else:
                turning_angle = 135
        # trouver la ligne
        elif lt_status_now == [0,0,0,0,0]:
            turning_angle = turning_angle

        fw.turn(math.radians(turning_angle), frame)

    def stop(self):
        self.move_at_distance(1, bw.speed > 0)

    # Déplacement d'une distance connue
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
        steering_angles = circ.steering_for_circumvention()

        for angle in steering_angles:
            bw.forward(frame)
            fw.turn(angle + (math.pi/2), frame)
            frame+= 1



car_controller = CarController()

# initialisation du véhicue
def init_objects(pos, rot):
    # init car position
    obj = bpy.data.objects[CAR_NAME]
    obj.animation_data_clear()
    obj.location = pos
    obj.rotation_euler = rot
    obj.keyframe_insert(data_path="rotation_euler", frame = 0)
    obj = bpy.data.objects[CAR_NAME]

# parcours avec courbes
def parcours1_widecurve():
    global frame
    init_objects((18,-1.9419,0.75), [EULER_X, EULER_Y, -EULER_Z])
    frame = 15
    bw.speed = 1.5

    while(frame < 2000):
        bw.forward(frame)
        car_controller.follow_line()
        frame += 1

# parcours avec arrêt
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

# parcours avec arrêt et retour arrière
def parcours3_moveback():
    global frame
    init_objects((0,0,0.75), [EULER_X, EULER_Y, -EULER_Z])
    frame = 15
    bw.speed = 2.5
    
    car_controller.move_at_distance(3, False)

# parcours avec évitement d'obstacle
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

# choix du parcours à réaliser, tout dépendant de la scène retirer un dièse(#) de commentaire
if __name__ == '__main__':
    parcours1_widecurve()
    #parcours2_stop()
    #parcours3_moveback()
    #parcours4_obstacle()