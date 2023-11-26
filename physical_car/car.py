from timeit import default_timer as timer
from time import sleep
from dataclasses import dataclass
from typing import Dict, List
import numpy as np
import csv
from datetime import datetime

from SunFounder_PiCar_S.example.SunFounder_Ultrasonic_Avoidance.Ultrasonic_Avoidance import Ultrasonic_Avoidance
from SunFounder_PiCar_S.example.SunFounder_Line_Follower.Line_Follower import Line_Follower
from SunFounder_PiCar.picar.back_wheels import Back_Wheels
from SunFounder_PiCar.picar.front_wheels import Front_Wheels
from module.us_filter import US_Filter
from module.angle_calculator import Angle_Calculator
from module.accelerator import Accelerator

# CONSTANTS
MAX_ACCEL = 0.01
MAX_SPEED = 0.23 # m/s
INTERVAL = 0.05 # seconds

@dataclass
class CarMeasurement:
    timestamp: float
    delta_time: float
    position_x: float
    position_y: float
    angle: float
    speed: float
    acceleration: float
    steering_angle: float
    distance_from_object_cm: float

    
    def header(self):
        return ["timestamp", "delta_time", "position_x", "position_y", "angle", "speed", "acceleration", "steering_angle", "distance_from_object (cm)"]


    def to_list(self):
        return [self.timestamp, self.delta_time, self.position_x, self.position_y, self.angle, self.speed, self.acceleration, self.steering_angle, self.distance_from_object_cm]


@dataclass
class CarMovement:
    speed: float # in meter per second
    steering_angle: float # in radian


class Car:


    def __init__(self):
        self._running = False
        self._movement = CarMovement(0, 0)

        self._position_x = 0
        self._position_y = 0
        self._angle = np.pi/2
        self._goal_speed = 0

        self._front_wheels = Front_Wheels()
        self._back_wheels = Back_Wheels()
        self._detector = Ultrasonic_Avoidance(20)
        self._detector_filter = US_Filter(64) # Taille de la fenetre
        self._line_follower = Line_Follower()
        self._angle_calculator = Angle_Calculator()
        self._accelerator = Accelerator(MAX_ACCEL, MAX_SPEED, INTERVAL)

        self._logger = CarLogger()
        self._movements_for_sample = {}

        self._engine_input_to_speed_coeffs = [-9.99328429e-10, -1.56940772e-08,  2.36553357e-05,  1.11620286e-03, -1.72643141e-04]
        self._speed_to_engine_input_coeffs = [-1.13689793e+04, 1.19347114e+04, -3.36017736e+03,  7.04488298e+02, 1.67142858e-01]    
        self._engine_to_speed = np.poly1d(self._engine_input_to_speed_coeffs)
        self._speed_to_engine = np.poly1d(self._speed_to_engine_input_coeffs)


        self._wheel_base = 0.14
        self._tire_width = 0.108
        pass

    @property
    def goal_speed(self):
        return self._goal_speed

    @goal_speed.setter
    def goal_speed(self, new_goal_speed):
        self._accelerator.max_speed = new_goal_speed
        self._goal_speed = new_goal_speed

    @property
    def movement(self):
        return self._movement


    @movement.setter
    def movement(self, new_movement:CarMovement):
        #assert new_movement.speed <= 0.23, f'Speed should not be higher than 0.23, found {new_movement.speed}'
        #assert new_movement.speed >= -0.23, f'Speed should not be lower than -0.23, found {new_movement.speed}'
        #assert new_movement.steering_angle <= 45, f'Steering angle should not be higher than 45°, found {new_movement.steering_angle}'
        #assert new_movement.steering_angle >= -45, f'Steering angle should not be lower than -45°, found {new_movement.steering_angle}'
        self._movement = new_movement
        self.apply_car_movement()


    def run(self):
        self._running = True
        while self._running:
            try:
                #self.loop()
                self.test_line_follower()
            except KeyboardInterrupt:
                self.stop()
        self.stop()


    def stop(self):
        self._running = False
        self.movement = CarMovement(0, 0)
        self._logger.dump_to_file()


    def test_line_follower(self):
        ir_status = self._line_follower.read_digital()
        last_steering_angle = self._logger.last_measurement().steering_angle
        new_angle = self._angle_calculator.get_steering_angle(ir_status, last_steering_angle)
        
        self.movement = CarMovement(0.1, new_angle)
        
        timestamp = timer()
        
        acceleration = self.calculate_acceleration(timestamp)
        self.calculate_position_and_angle(timestamp)
        self._logger.add(CarMeasurement(timestamp=timestamp,
                                       position_x=self._position_x,
                                       position_y=self._position_y,
                                       angle = self._angle,
                                       speed=self.movement.speed,
                                       acceleration=acceleration,
                                       steering_angle=self.movement.steering_angle,
                                       distance_from_object_cm=0))
        
    def loop(self):
        # distance_from_object_cm = self.get_distance_from_object()
        distance_from_object_cm = 100
        if(distance_from_object_cm <= 1):
            self._running = False
        else:
            next_speed = self._accelerator.speed_to_accel(self.last_speed())
            new_movement = CarMovement(next_speed, 0)
            self.movement = new_movement

        timestamp = timer()
        
        acceleration = self.calculate_acceleration(timestamp)
        self.calculate_position_and_angle(timestamp)
        self._logger.add(CarMeasurement(timestamp=timestamp,
                                        delta_time = timestamp - self.last_measurement().timestamp,
                                       position_x=self._position_x,
                                       position_y=self._position_y,
                                       angle = self._angle,
                                       speed=self.movement.speed,
                                       acceleration=acceleration,
                                       steering_angle=self.movement.steering_angle,
                                       distance_from_object_cm=distance_from_object_cm))

        delta_time = timer() - self.last_measurement().timestamp
        if(delta_time <= INTERVAL):
            sleep(INTERVAL - delta_time)

        self._logger.dump_to_file()

    def get_distance_from_object(self):
        raw_distance = self._detector.get_distance()
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
        if self.movement.speed < 0:
            self._back_wheels.forward() # Forward et Backward sont inversés
        else:
            self._back_wheels.backward()
            
        speed_right = self._speed_to_engine(np.abs(self.movement.speed))
        speed_left = self._speed_to_engine(np.abs(self.movement.speed))
        
        self._front_wheels.turn(np.rad2deg(- self.movement.steering_angle) + 90)
            
        self._back_wheels.speed_left = np.rint(speed_left)
        self._back_wheels.speed_right = np.rint(speed_right)
        

    def speed_m_per_s_to_motor_percentage(self, speed_m_per_s):
        return 1/self.speed_fitter_function(speed_m_per_s)


class CarLogger:
    def __init__(self):
        self._data: List[CarMeasurement] = [CarMeasurement(timer(),0,0,0,0,0,0,0,-1)]


    @property
    def data(self):
        return self._data


    def add(self, measurement:CarMeasurement):
        self._data.append(measurement)


    def last_measurement(self):
        return self._data[-1]
    

    def dump_to_file(self):
        file_name = datetime.now().strftime("%Y%m%d%H%M%S.csv")
        with open(file_name, mode="w") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(CarMeasurement.header(self))
            for measurement in self.data:
                writer.writerow(measurement.to_list())

if __name__ == "__main__":
    i = 0
    car = Car()
    car.goal_speed = MAX_SPEED

    while(i < 50):
        car.loop()
        i += 1


