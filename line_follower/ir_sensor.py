import bpy
from mathutils import Vector

class Sensor:
    def __init__(self):
        self._sensor_name = None  # Initialize the sensor_name to None

    def __init__(self, new_name):
        self._sensor_name = new_name

    # Getter method for sensor_name
    def get_sensor_name(self):
        return self._sensor_name

    # Setter method for sensor_name
    def set_sensor_name(self, new_name):
        if isinstance(new_name, str):
            self._sensor_name = new_name
        else:
            print("Invalid sensor name. Please provide a valid string.")
    
    # Raycast from the sensors position to detect any object in the -Z direction
    # The function returns the rgba color of the object detected
    def detect_color(self):
        # Get sensor by name and get pcb_ir location (parent object)
        sensor = bpy.data.objects.get(self._sensor_name)
        
        # Create direction for the raycast and the origin from where the raycast start
        ray_direction = Vector((0, 0, -1))
        ray_origin = sensor.matrix_world.translation + sensor.dimensions[2] * ray_direction
        
        # Scene raycast
        depsgraph = bpy.context.evaluated_depsgraph_get()
        result, location, normal, index, object, matrix = bpy.context.scene.ray_cast(depsgraph, ray_origin, ray_direction)
        
        # If raycast hit something, returns color of the object detected
        if result:
            r = object.data.materials[0].diffuse_color[0]
            g = object.data.materials[0].diffuse_color[1]
            b = object.data.materials[0].diffuse_color[2]
            return [r, g, b]
