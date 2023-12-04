from timeit import default_timer as timer
from time import sleep
from dataclasses import dataclass
from typing import Dict, List
import numpy as np
import csv
from datetime import datetime
from time import sleep
from enum import Enum

from SunFounder_Module.picar_s.Ultrasonic_Avoidance import Ultrasonic_Avoidance
from SunFounder_Module.picar_s.Line_Follower import Line_Follower
from SunFounder_Module.picar.back_wheels import Back_Wheels
from SunFounder_Module.picar.front_wheels import Front_Wheels
from module.us_filter import US_Filter
from module.angle_calculator import Angle_Calculator
from module.accelerator import Accelerator
from module.circumvention import Circumvention

# CONSTANTS
MAX_ACCEL = 0.22
MAX_SPEED = 0.1 # m/s
INTERVAL = 0.1 # seconds
MINIMUM_SPEED = 0.03
MAX_OBSTACLE_DIST_CM = 13

CIRCUMVENTION_SPEED = 0.1

class Parcour(Enum):
    BACKWARD = 1
    STOP = 2
    CURVE = 3
    OBSTACLE = 4

@dataclass
class CarMeasurement:
    timestamp: float
    position_x: float
    position_y: float
    angle: float
    speed: float
    acceleration: float
    steering_angle: float
    distance_from_object_cm: float

    
    def header(self):
        return ["timestamp", "position_x", "position_y", "angle", "speed", "acceleration", "steering_angle", "distance_from_object (cm)"]


    def to_list(self):
        return [self.timestamp, self.position_x, self.position_y, self.angle, self.speed, self.acceleration, self.steering_angle, self.distance_from_object_cm]


@dataclass
class CarMovement:
    speed: float # in meter per second
    steering_angle: float # in radian


class Car:


    def __init__(self):
        self._running = False
        self._movement = CarMovement(0, 0)
        
        self._wheel_base = 0.14
        self._tire_width = 0.108

        self._position_x = 0
        self._position_y = 0
        self._angle = np.pi/2
        
        self._max_speed = MAX_SPEED
        self._goal_speed = self._max_speed
        self._max_accel = MAX_ACCEL

        self._front_wheels = Front_Wheels()
        self._back_wheels = Back_Wheels()
        self._detector = Ultrasonic_Avoidance(20)
        self._detector_filter = US_Filter(4) # Taille de la fenêtre
        self._line_follower = Line_Follower()
        
        self._angle_calculator = Angle_Calculator()
        self._accelerator = Accelerator(self._max_accel, self._goal_speed, INTERVAL, self._max_speed)
        
        self.default_object_size = 0.27 # Taille par défaut que le char va éviter (meters)
        self._circumvention_module = Circumvention(self._wheel_base, self._tire_width, self.default_object_size)

        self._logger = CarLogger()
        self._future_movements = []

        self._engine_input_to_speed_coeffs = [-9.99328429e-10, -1.56940772e-08,  2.36553357e-05,  1.11620286e-03, -1.72643141e-04]
        self._speed_to_engine_input_coeffs = [-1.13689793e+04, 1.19347114e+04, -3.36017736e+03,  7.04488298e+02, 1.67142858e-01]    
        self._engine_to_speed = np.poly1d(self._engine_input_to_speed_coeffs)
        self._speed_to_engine = np.poly1d(self._speed_to_engine_input_coeffs)
        self._is_bypassed = False

        self._sampling_time = INTERVAL

    @property
    def goal_speed(self):
        return self._goal_speed

    @goal_speed.setter
    def goal_speed(self, new_goal_speed):
        self._accelerator.goal_speed = new_goal_speed
        self._goal_speed = new_goal_speed

    @property
    def movement(self):
        return self._movement


    @movement.setter
    def movement(self, new_movement:CarMovement):
        assert new_movement.speed <= 0.23, f'Speed should not be higher than 0.23, found {new_movement.speed}'
        assert new_movement.speed >= -0.23, f'Speed should not be lower than -0.23, found {new_movement.speed}'
        self._movement = new_movement
        self.apply_car_movement()


    def run(self):
        self._running = True
            
        while self._running:
            try:
                self.loop()
            except KeyboardInterrupt:
                self.stop()
        self.stop()


    def stop(self):
        try:
            self.goal_speed = 0
        
            next_speed = self._accelerator.get_next_speed(self.last_speed())
            while(next_speed > 0):
                self.movement = CarMovement(next_speed, 0)
                next_speed = self._accelerator.get_next_speed(self.last_speed())
                self._loop_footer()
        except:
            pass
        self.movement = CarMovement(0, 0)
        self._running = False
        self._logger.dump_to_file()

        
    def loop(self):
        """
        Mouvement par défaut pour satisfaire les dieux
        """
        new_movement = self.movement
        distance_from_object_cm = self._detector_filter.prev_ma

        """
        Boucle alternative
        """
        if self._is_bypassed:
            new_movement = self.bypassed_logic()
            if (not self._is_bypassed):
                self.goal_speed = self._max_speed
        
        """
        Boucle générale
        """
        if not self._is_bypassed:
            """
            Données des senseurs
            """
            distance_from_object_cm = self.get_distance_from_object()
            if(distance_from_object_cm <= 40):
                need_to_stop = self._is_object_too_close(distance_from_object_cm) or self._accelerator.determine_stopping_dist(0 if self._is_object_too_close(distance_from_object_cm) else distance_from_object_cm - MAX_OBSTACLE_DIST_CM, self.last_speed())
                if(need_to_stop):
                    is_droite = self._logger.last_measurement().steering_angle < 0

                    self._prepare_to_circumvention(is_droite)
                    self._do_circumvention(is_droite)

                else:
                    new_movement = self._follow_line_movement()
                    
            else:
                new_movement = self._follow_line_movement()
                
        self.movement = new_movement
        
        self._loop_footer()
        
    def _follow_line_movement(self):
        next_speed = self._accelerator.get_next_speed(self.last_speed())
        
        ir_status = self._line_follower.read_digital()
        last_steering_angle = self._logger.last_measurement().steering_angle
        #print("gros last steering tbk")
        #print(last_steering_angle)
        new_angle = self._angle_calculator.get_steering_angle(ir_status, last_steering_angle)
        
        if (np.sum(ir_status) >= 3):
            print("J'ai vu la ligne")
            self._running = False
        
        return CarMovement(next_speed, new_angle)
    
    def _is_object_too_close(self, distance_from_object_cm):
        return distance_from_object_cm <= MAX_OBSTACLE_DIST_CM
    
    def _prepare_to_circumvention(self, is_droite):
        #deccel
        self._future_movements.extend([CarMovement(speed, 0) for speed in self._accelerator.get_stop_speeds_list(self.last_speed())])

        #stop
        self._future_movements.extend([CarMovement(0, 0) for _ in range(20)])

        #backward
        backward_dist_m = 0.335
        backward_angle = -0.15
        #backward_angle = 0.15 if is_droite else -0.15
        self._future_movements.extend([CarMovement(speed, backward_angle) for speed in self._accelerator.get_speeds_list_for_travel(backward_dist_m)])

        #stop
        self._future_movements.extend([CarMovement(0, 0) for _ in range(20)])

        #accel
        self.goal_speed = CIRCUMVENTION_SPEED
        accel_speeds = self._accelerator.get_speeds_to_accel()
        self._future_movements.extend([CarMovement(speed, 0) for speed in accel_speeds])
        
        self._is_bypassed = True
        
    def _do_circumvention(self, is_droite):
        self._angle_calculator.reset_off_track_count()

        # circumvention
        angles = self._circumvention_module.steering_for_circumvention(0.7, self._sampling_time, 0.1, 0.24)

        future_movements = []
        for angle in angles:
            future_movements.append(CarMovement(self.goal_speed, angle)) 
            #future_movements.append(CarMovement(self.goal_speed, -angle if is_droite else angle)) 
        self._future_movements.extend(future_movements)
        self._is_bypassed = True

        
    def _loop_footer(self):
        
        """
        Fréquences d'échantillonnages uniformes
        """
        delta_time = timer() - self._logger.last_measurement().timestamp
        if(delta_time < self._sampling_time):
            sleep(self._sampling_time - delta_time)

        """
        Temps de la boucle
        """
        timestamp = timer()

        """
        Calculation nécessitant le temps
        """
        acceleration = self.calculate_acceleration(timestamp)
        self.calculate_position_and_angle(timestamp)

        """
        Journalisation
        """
        self._logger.add(CarMeasurement(timestamp=timestamp,
                                       position_x=self._position_x,
                                       position_y=self._position_y,
                                       angle = self._angle,
                                       speed=self.movement.speed,
                                       acceleration=acceleration,
                                       steering_angle=self.movement.steering_angle,
                                       distance_from_object_cm=0))
        

    def bypassed_logic(self):
        if(len(self._future_movements) != 0):
            new_movement = self._future_movements.pop(0)
        else:
            self._is_bypassed = False
            return self.movement
        return new_movement


    def get_distance_from_object(self):
        raw_distance = self._detector.distance()
        if raw_distance == -1:
            return self._detector_filter.prev_ma
        return self._detector_filter.filter_stream(raw_distance)
            

    def calculate_acceleration(self, timestamp):
        last_speed = self._logger.last_measurement().speed
        last_timestamp = self._logger.last_measurement().timestamp
        return (self.movement.speed-last_speed)/(timestamp - last_timestamp)
    

    def calculate_position_and_angle(self, timestamp):
        seconds_elapsed = timestamp - self.last_measurement().timestamp
        if(self.movement.steering_angle != 0):
            turning_radius_m = (self._wheel_base / np.sin(np.abs(self.movement.steering_angle))) + (self._tire_width/2)
            turning_circumference_m = 2 * np.pi * turning_radius_m
            circle_traveled_ratio = (self.movement.speed*seconds_elapsed) / turning_circumference_m
            angle_traveled_r = circle_traveled_ratio*2*np.pi

            if(angle_traveled_r < 0):
                self._angle = self._angle-angle_traveled_r
            else:
                self._angle = self._angle+angle_traveled_r

        distance_traveled = self.movement.speed*seconds_elapsed
        delta_position_x=np.cos(self._angle)*distance_traveled
        delta_position_y=np.sin(self._angle)*distance_traveled
        self._position_x+=delta_position_x
        self._position_y+=delta_position_y

    def last_measurement(self):
        return self._logger.last_measurement()
        
    def last_speed(self):
        return self.last_measurement().speed

    def apply_car_movement(self):
        print(self.movement)
        if self.movement.speed < 0:
            self._back_wheels.forward() # Forward et Backward sont inversés
        else:
            self._back_wheels.backward()
        
        speed_right = self._speed_to_engine(np.abs(self.movement.speed))
        speed_left = self._speed_to_engine(np.abs(self.movement.speed))
        
        if self._angle_calculator.is_off_track():
            if self.movement.steering_angle < np.deg2rad(-40):
                speed_left = self._speed_to_engine(MINIMUM_SPEED)
            elif self.movement.steering_angle > np.deg2rad(40):
                speed_right = self._speed_to_engine(MINIMUM_SPEED)
                
        self._front_wheels.turn(np.rad2deg(- self.movement.steering_angle) + 90)
        self._back_wheels.speed_left = np.rint(speed_left)
        self._back_wheels.speed_right = np.rint(speed_right)
        

class CarLogger:
    def __init__(self):
        self._data: List[CarMeasurement] = [CarMeasurement(timer(),0,0,0,0,0,0,-1)]


    @property
    def data(self):
        return self._data


    def add(self, measurement:CarMeasurement):
        self._data.append(measurement)


    def last_measurement(self):
        return self._data[-1]
    

    def dump_to_file(self):
        file_name = f"data/{datetime.now().strftime('%Y%m%d%H%M%S.csv')}"
        with open(file_name, mode="w") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(CarMeasurement.header(self))
            for measurement in self.data:
                writer.writerow(measurement.to_list())

def main():
    car = Car()
    car.run()
    

if __name__ == "__main__":
    main()

