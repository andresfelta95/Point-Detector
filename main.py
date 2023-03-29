# Author: Andres Tangarife
# Date: 2023-03-02
# Description: This is a demo to use 10 ultrasonic sensors to detect darts in a
#              dartboard. The sensors are connected to a Multiplexer to reduce
#              the number of pins used in the ESP32.
#              The sensors are connected to the Multiplexer as follows:
#              - Sensor 1: Channel 0
#              - Sensor 2: Channel 1
#              - Sensor 3: Channel 2
#              - Sensor 4: Channel 3
#              - Sensor 5: Channel 4
#              - Sensor 6: Channel 5
#              - Sensor 7: Channel 6
#              - Sensor 8: Channel 7
#              - Sensor 9: Channel 8
#              - Sensor 10: Channel 9
#              The ESP32 is connected to the Multiplexer as follows:
#              - S0: Pin 18 (past 4) 
#              - S1: Pin 5 
#              - S2: Pin 17 (past 18)
#              - S3: Pin 16 (past 19)
#              - E: Pin 19 (past 23)
#              The ESP32 is connected to the OLED display as follows:
#              - SDA: Pin 21
#              - SCL: Pin 22
#              - VCC: 3.3V
#              - GND: GND
#              The echo pin of the sensors is connected to the ESP32 as follows:
#              - Sensor 1: Pin 13 (past 32)
#              - Sensor 2: Pin 12 (past 33)
#              - Sensor 3: Pin 14 (past 25)
#              - Sensor 4: Pin 27 (past 26)
#              - Sensor 5: Pin 26 (past 27)
#              - Sensor 6: Pin 25 (past 14)
#              - Sensor 7: Pin 33 (past 12)
#              - Sensor 8: Pin 32 (past 13)
#              - Sensor 9: Pin 35
#              - Sensor 10: Pin 34
#              The trigger pin for the multiplexer is connected to the ESP32 as follows:
#              - Pin 4 (past 15)
# Import the libraries
# from ssd1306 import SSD1306_I2C
from machine import Pin, time_pulse_us
import time
from mux import Mux
from ultraSensor import UltraSensor
import math

# Create the Multiplexer object
mux = Mux(18, 5, 17, 16, 19)

# Create the I2C object
# i2c = I2C(scl=Pin(22), sda=Pin(21))

# Create the OLED object
# oled = SSD1306_I2C(128, 32, i2c)

#Setting the trigger 
trig = Pin(4, Pin.OUT) #was pin 15 

# Sound_SPEED = 34300 #cm/s
# TRIG_PULSE_DURATION_US = 10

# Create the sensors objects
sensor0 = UltraSensor(13, 0, 19.8, 0.0161, 1.6172) # Pin 13 , location (0,19.8)
sensor1 = UltraSensor(12, 11.4, 16.2, 0.0158, 1.7105) # Pin 12 , location (11.4,16.2)
sensor2 = UltraSensor(14, 18.8, 6, 0.016, 1.9421) # Pin 14 , location (18.8,6)
sensor3 = UltraSensor(27, 18.8, -6, 0.0158, 2.1619) # Pin 27 , location (18.8,-6)
sensor4 = UltraSensor(26, 11.4, -16.2, 0.0153, 2.294) # Pin 26 , location (11.4,-16.2)
sensor5 = UltraSensor(25, 0, -19.8, 0.0158, 1.1089) # Pin 25 , location (0,-19.8)
sensor6 = UltraSensor(33, -11.4, -16.2, 0.0164, 1.1967) # Pin 33 , location (-11.4,-16.2)
sensor7 = UltraSensor(32, -18.8, -6, 0.0152, 1.8608) # Pin 32 , location (-18.8,-6)
sensor8 = UltraSensor(35, -18.8, 6, 0.0154, 1.9196) # Pin 35 , location (-18.8,6)
sensor9 = UltraSensor(34, -11.4, 16.2, 0.0158, 1.7896) # Pin 34 , location (-11.4,16.2)

# Create the list of sensors
sensors = [sensor0, sensor1, sensor2, sensor3, sensor4, sensor5, sensor6, sensor7, sensor8, sensor9]

#points (sending the data one at a time)
player1_points = 0
player2_points = 0

""" This function will read the disance from the sensor and return the distance in cm
    it will read the distance 100 times and return the average but ignore the first 10 readings
    Parameters: echo - the echo pin of the sensor
    Returns: distance in cm
"""
# def read_distance(echo):
#     distance_cm = 0
#     for i in range(10):
#         trig.value(0)
#         time.sleep_us(5)
#         trig.value(1)
#         time.sleep_us(TRIG_PULSE_DURATION_US)
#         trig.value(0)
#         ultrason_duration = time_pulse_us(echo, 1, 50000)
#         if i > 0:
#             #   cm = duration * speed of sound(cm/s) / 2 (round trip) / 10000 (us to s)
#             distance_cm += Sound_SPEED * ultrason_duration /2 / 1000000
#         time.sleep_us(100)
#     distance_cm = distance_cm / 9
#     #rounding the distance to no decimal places and adding 1 to get the middle of the dart(exact distance)
#     distance_cm = distance_cm + 1.2
#     return distance_cm   

    

while True:
    #   Read the distance from each sensor
    for i in range(len(sensors)):
        sensor = sensors[i]
        mux.set_channel(i)
        distance = sensor.read_distance()
        print("Sensor: ", i, " Distance: ", distance)
        time.sleep(0.1)
    # sensor = sensors[9]
    # mux.set_channel(9)
    # distance = sensor.read_distance()
    # print("Sensor: ", 9, " Distance: ", distance)
    # time.sleep(1)

def findingTheDart(dartList):
    position = 0

    #for dart_pos in dartList:
    
    return position

