"""
This module contains the class for the ultrasonic sensor using the HC-SR04 with interrupts and the clock to avoid blocking the main loop
and avoid noise in the readings.
each sensor will have the following attributes:
    * echo - the echo pin of the sensor
    * trig - the trig pin of the sensor (pin 4 for all sensors)
    * location - x, y coordinates of the sensor in cm from the center of the board
    * distance - the distance in cm with 2 decimal places

Author: Andres Tangarife - Keven Lou
Date: 2023-03-17
"""

# Import the libraries
from machine import Pin, time_pulse_us
import time
import uasyncio as asyncio
import math
from mux import Mux

Sound_SPEED = 34300 #cm/s

# Create the class
class UltraSensor:

    #   Initialize the sensor
    def __init__(self, echo, _x, _y, _Mval, _Bval):
        #   Set the attributes
        self._echo = Pin(echo, Pin.IN)
        self._trig = Pin(4, Pin.OUT)
        self._trig.value(0)
        #   Set the location of the sensor as a tuple
        self._location = (_x, _y)
        self._Mval = _Mval
        self._Bval = _Bval
        self.distance = 0.0
        self._timeOut = 50000 #   Timeout in us for the echo pulse
        self._sleep = 0.1 #   Sleep time in s between readings
        self._iterations = 30 #   Number of iterations to get the average distance
        self._perFail = 0.66 #   Percentage of failed readings to consider the sensor as failed


    #   This function will read the distance from the sensor and return the distance in cm
    def read_distance(self):
        distances = []
        for i in range(self._iterations):
            self._trig.value(0)
            time.sleep_us(2)
            self._trig.value(1)
            time.sleep_us(10)
            self._trig.value(0)
            try:
                #   Get the duration of the echo pulse
                ultrason_duration = time_pulse_us(self._echo, 1, self._timeOut)
            except OSError:
                ultrason_duration = 0
            if ultrason_duration > 0:
                #   cm = duration * speed of sound(cm/s) / 2 (round trip) / 10000 (us to s)
                #distances.append(Sound_SPEED * ultrason_duration /2.0 / 1000000)
                distances.append(ultrason_duration) #   In us
            time.sleep_ms(10)
        #   Remove the outliers
        while len(distances) >= 7:
            #   Remove the lowest and highest values
            distances.remove(min(distances))
            distances.remove(max(distances))
        print(distances)
        cm = sum(distances) / len(distances)
        cm = self.convert_Distance(cm)
        #   Return the average distance
        return round(cm, 2)
    
    def convert_Distance(self, distance):
        # actualDistance = 0.0161 * distance + 1.6172 # sensor 0
        # actualDistance = 0.0158 * distance + 1.7105 # sensor 1
        # actualDistance = 0.016 * distance + 1.9421 # sensor 2
        # actualDistance = 0.0158 * distance + 2.1619 # sensor 3
        # actualDistance = 0.0153 * distance + 2.294 # sensor 4
        # actualDistance = 0.0158 * distance + 1.1089 # sensor 5
        # actualDistance = 0.0164 * distance + 1.1967 # sensor 6
        # actualDistance = 0.0152 * distance + 1.8608 # sensor 7
        # actualDistance = 0.0154 * distance + 1.9196 # sensor 8
        # actualDistance = 0.0157 * distance + 1.7885 # sensor 9
        actualDistance = self._Mval * distance + self._Bval
        return actualDistance
    
#   Manager Class for the sensors
class UltraManager:
    """
    This class will manage a list of sensors and will return the distance of the closest object

    Attributes:
        *   sensors - list of sensors
        *   multi - multiplexer object  
    """

    def __init__(self, sensors, multi):
        self._sensors = sensors
        self._multi = multi
        self._distances = []
        self._sleep = 0.1
        self._iterations = 30
        self._perFail = 0.66
        self._timeOut = 50000

    #   Function to read all sensors and return a list of distances
    def read_distances(self):
        distances = []
        for i in range(len(self._sensors)):
            self._multi.set_channel(i)
            #   Create a loop, if the sensor gets the same reading 3 times in a row, append the distance to the list and break the loop
            count = 0
            while count < 3:
                distance = self._sensors[i].read_distance()
                if distance == self._distances[i]:
                    count += 1
                else:
                    count = 0
                self._distances[i] = distance
            distances.append(distance)
            #   Print the distance
            print("Sensor: ", i, " Distance: ", distance)
            #   Sleep for the specified time
            time.sleep(self._sleep)
        return distances
