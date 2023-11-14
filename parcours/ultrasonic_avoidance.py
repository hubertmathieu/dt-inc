import bpy
import math
from mathutils import Vector

class Ultrasonic_Avoidance(object):
    def __init__(self, us_sensor_name):
        self.angle = math.radians(90)
        self.us_sensor_obj = bpy.data.objects[us_sensor_name]

# return distance: succès
# return -1 : échec
    def distance(self):
        xc,yc,zc = self.us_sensor_obj.matrix_world.translation
        lcx,lcy,lcz = self.us_sensor_obj.dimensions
        axc,ayc,azc = self.us_sensor_obj.rotation_euler

        #long: longueur du laser
        long = 30
        
        # position finale du laser
        xlf = long * math.cos(azc + self.angle)
        ylf = long * math.sin(azc + self.angle)
        direction = Vector((xlf, ylf, 0))
        
        # position initiale du laser
        #xli = xc + (1 + lcx/2) * math.cos(azc - self.angle)
        #yli = yc + (1 + lcx/2) * math.sin(azc - self.angle)

        xli = xc + 5 * math.cos(azc + self.angle)
        yli = yc + 5 * math.sin(azc + self.angle)
        origin = Vector((xli, yli, 1))

        distance_between = (self.us_sensor_obj.matrix_world.translation - origin)

        # hit: booléen si ça touche qqchose
        # hit_location: vecteur xyz où ça touche. 0,0,0 si hit faux
        # object: objet obstacle qui est frappé
        depsgraph = bpy.context.evaluated_depsgraph_get()
        hit, hit_location, normal, index, object, matrix = bpy.context.scene.ray_cast(depsgraph, origin, direction)
        
        if hit:
            # distance: float distance entre le cube et le point de contact
            distance = (self.us_sensor_obj.matrix_world.translation - hit_location - distance_between).length 
            return distance
        else:
            return -1

    def get_distance(self):
        return self.distance()

    def less_than(self, alarm_gate):
        dis = self.get_distance()
        status = 0
        if dis >=0 and dis <= alarm_gate:
            status = 1
        elif dis > alarm_gate:
            status = 0
        else:
            status = -1
        #print('distance =',dis)
        #print('status =',status)
        return status