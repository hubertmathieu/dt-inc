import bpy
from mathutils import Vector

# Classe utilisée pour créer un objet de capteur infrarouge
class Ir_Sensor:

    def __init__(self, new_name):
        self._sensor_name = new_name

    # Retourne le nom du capteur
    def get_sensor_name(self):
        return self._sensor_name

    # Initialise le nouveau nom du capteur
    def set_sensor_name(self, new_name):
        if isinstance(new_name, str):
            self._sensor_name = new_name
        else:
            print("Invalid sensor name. Please provide a valid string.")
    
    # La fonction utilise le raycast, un vecteur qui pointe vers -Z. Le vecteur retourne les données lorsqu'un object est détecté
    # La fonction retourne la couleur RGB de l'objet
    def detect_color(self):
        # Get le capteur dans blender en fonction du nom
        sensor = bpy.data.objects.get(self._sensor_name)
        
        # Créer une direction pour le vecteur et le point d'origine il commence
        ray_direction = Vector((0, 0, -1))
        ray_origin = sensor.matrix_world.translation + sensor.dimensions[2] * ray_direction
        
        # Applique le raycast depuis la scene principal blender
        depsgraph = bpy.context.evaluated_depsgraph_get()
        result, location, normal, index, object, matrix = bpy.context.scene.ray_cast(depsgraph, ray_origin, ray_direction)
        
        # Si un objet est détecté, retourne la couleur
        if result:
            r = object.data.materials[0].diffuse_color[0]
            g = object.data.materials[0].diffuse_color[1]
            b = object.data.materials[0].diffuse_color[2]
            return [r, g, b]
