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
        self._iterations = 100 #   Number of iterations to get the average distance
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
            #time.sleep_us(50)
        #   Remove the outliers
        while len(distances) >= 90:
            #   Remove the lowest and highest values
            distances.remove(min(distances))
            distances.remove(max(distances))
        # print(distances)
        cm = sum(distances) / len(distances)
        cm = (cm * 340 / 20000) + 1.7
        #   Return the average distance
        return round(cm, 4)
    
    # def convert_Distance(self, distance):
    #     # actualDistance = 0.0161 * distance + 1.6172 # sensor 0
    #     # actualDistance = 0.0158 * distance + 1.7105 # sensor 1
    #     # actualDistance = 0.016 * distance + 1.9421 # sensor 2
    #     # actualDistance = 0.0158 * distance + 2.1619 # sensor 3
    #     # actualDistance = 0.0153 * distance + 2.294 # sensor 4
    #     # actualDistance = 0.0158 * distance + 1.1089 # sensor 5
    #     # actualDistance = 0.0164 * distance + 1.1967 # sensor 6
    #     # actualDistance = 0.0152 * distance + 1.8608 # sensor 7
    #     # actualDistance = 0.0154 * distance + 1.9196 # sensor 8
    #     # actualDistance = 0.0157 * distance + 1.7885 # sensor 9
    #     actualDistance = self._Mval * distance + self._Bval
    #     return actualDistance
    
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
            distance = self._sensors[i].read_distance()
            distances.append(distance)
            #   Print the distance
            print("Sensor: ", i, " Distance: ", distance)
            #   Sleep for the specified time
            # time.sleep_us(50)
            self._distances = distances
        return distances
    
    #   Function to get the 2 adjacent sensors to the closest object
    def get_adjacent_sensors(self):
        #   Get the index of the sensor with the smallest distance
        index = self._distances.index(min(self._distances))
        #   Check one sensor to the left and one to the right and pick the one with the smallest distance
        if index == 0:
            #   If the index is 0, then the sensor to the left is the last sensor
            left = len(self._distances) - 1
            right = index + 1
        elif index == len(self._distances) - 1:
            #   If the index is the last sensor, then the sensor to the right is the first sensor
            left = index - 1
            right = 0
        else:
            left = index - 1
            right = index + 1
        #   Check if right and left distances are more than 30 cm
        if self._distances[left] > 30 and self._distances[right] > 30:
            #   If both are more than 30 cm, then return the same sensor
            return index, index
        else:
            #   Check which sensor has the smallest distance
            if self._distances[left] < self._distances[right]:
                return left, index
            else:
                return index, right
        
    #   Function to get the location of the closest object
    def get_location(self):
        #   Get the 2 adjacent sensors to the closest object
        left, right = self.get_adjacent_sensors()
        #   Check if the 2 sensors are the same
        if left == right:
            #   Get the x and y coordinates from the sensor
            x1, y1 = self._sensors[left]._location
            #   Get the distance from the sensor
            r1 = self._distances[left]
            #   Calculate the distance from the center (0, 0) and the sensor
            d = math.sqrt(x1**2 + y1**2)
            #   Get second radius
            r2 = d - r1
            # Calculate the intersection points of the two circles
            a = (r1**2 - r2**2 + d**2) / (2*d)
            h = 0
            x3 = x1 + a*(0 - x1)/d
            y3 = y1 + a*(0 - y1)/d
            #   Circle Intersections
            rX1 = x3 + h*(0 - y1)/d
            rY1 = y3 - h*(0 - x1)/d
            rX2 = x3 - h*(0 - y1)/d
            rY2 = y3 + h*(0 - x1)/d
            #   Check which point is inside the board and return it
            if self.is_inside_board(rX1, rY1):
                return (rX1, rY1)
            else:
                return (rX2, rY2)
        #   Get the x and y coordinates from the sensors
        x1, y1 = self._sensors[left]._location
        x2, y2 = self._sensors[right]._location
        #   Get the distance from the sensors
        r1 = self._distances[left]
        r2 = self._distances[right]
        # Calculate the distance between the centers of the two circles
        d = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        

        # Check if the two circles overlap or are disjoint
        if d > r1 + r2:
            return "The circles are disjoint"
        elif d < abs(r1 - r2):
            return "One circle is inside the other"

        # Calculate the intersection points of the two circles
        a = (r1**2 - r2**2 + d**2) / (2*d)
        h = math.sqrt(r1**2 - a**2)
        x3 = x1 + a*(x2 - x1)/d
        y3 = y1 + a*(y2 - y1)/d
        #   Circle Intersections
        rX1 = x3 + h*(y2 - y1)/d
        rY1 = y3 - h*(x2 - x1)/d
        rX2 = x3 - h*(y2 - y1)/d
        rY2 = y3 + h*(x2 - x1)/d

        #   Check which point is inside the board and return it
        if self.is_inside_board(rX1, rY1):
            return (rX1, rY1)
        else:
            return (rX2, rY2)
        
    #   Function to check if a point is inside the board
    def is_inside_board(self, x, y):
        #   Check if the point is inside the board
        if x >= -20 and x <= 20 and y >= -20 and y <= 20:
            return True
        else:
            return False
        
    #   Function that will get two lists of distances and check if they are the same within a certain threshold
    def check_same(self, list1, list2):
        #   Check if the lists are the same length
        if len(list1) != len(list2):
            return False
        #   Check if the values are the same within a certain threshold (1 cm)
        for i in range(len(list1)):
            if abs(list1[i] - list2[i]) > 1:
                return False
        return True
    
    #   Function that will get two lists of distances and check if they are the same within a certain threshold
        
