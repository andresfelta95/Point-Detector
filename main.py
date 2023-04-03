"""
    Author: Andres Tangarife
    Date: 2023-03-29
    Description: This program will be used to play the dart game.
        This program will have the following states:
            - NoGame:       The game is not being played, Keep asking to the server for a new game
                            This state will finish when the server sends a new game 
            - ClearBoard:   Check until the reading of all the sensors is more than 35 cm

            - GameDart1:    Gets the location of the first dart, and sends it to the server
                            After 10 if the dart is not in the board sends false to the server
            - GameDart2:    Gets the location of the second dart, and sends it to the server
                            After 10 if the dart is not in the board sends false to the server
            - GameDart3:    Gets the location of the third dart, and sends it to the server
                            After 10 if the dart is not in the board sends false to the server

            - NextTurn:     Will ask the server for if a new turn is available, if it is, then it will
                            move to the ClearBoard state, if not, then it will move to the NoGame state


        The sensors are connected to the Multiplexer as follows:
            - Sensor 0: Channel 0
            - Sensor 1: Channel 1
            - Sensor 2: Channel 2
            - Sensor 3: Channel 3
            - Sensor 4: Channel 4
            - Sensor 5: Channel 5
            - Sensor 6: Channel 6
            - Sensor 7: Channel 7
            - Sensor 8: Channel 8
            - Sensor 9: Channel 9
        The ESP32 is connected to the Multiplexer as follows:
            - S0: Pin 18 (past 4) 
            - S1: Pin 5 
            - S2: Pin 17 (past 18)
            - S3: Pin 16 (past 19)
            - E: Pin 19 (past 23)
        The echo pin of the sensors is connected to the ESP32 as follows:
            - Sensor 0: Pin 13 (past 32)
            - Sensor 1: Pin 12 (past 33)
            - Sensor 2: Pin 14 (past 25)
            - Sensor 3: Pin 27 (past 26)
            - Sensor 4: Pin 26 (past 27)
            - Sensor 5: Pin 25 (past 14)
            - Sensor 6: Pin 33 (past 12)
            - Sensor 7: Pin 32 (past 13)
            - Sensor 8: Pin 35
            - Sensor 9: Pin 34
        The trigger pin for the multiplexer is connected to the ESP32 as follows:
            - Pin 4 (past 15)
        The ESP32 will connect to the server via WiFi
"""

# Import the libraries
from machine import Pin, time_pulse_us
import time
from mux import Mux
from ultraSensor import *
import math
import network

# Create the Multiplexer object
mux = Mux(18, 5, 17, 16, 19)

#Setting the trigger 
# trig = Pin(4, Pin.OUT) #was pin 15 

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

#   Create Sensor Manager
sensor_manager = UltraManager(sensors, mux)

# Create an enum for the states
class State:
    NoGame = 0
    ClearBoard = 1
    GameDart1 = 2
    GameDart2 = 3
    GameDart3 = 4
    NextTurn = 5

# Create the variables for the states
state = State.NoGame
previous_state = State.NoGame

# Create the game variables
game = False
turn = False
dart = 0
dart1 = False
dart2 = False
dart3 = False
dart1_location = (0,0)
dart2_location = (0,0)
dart3_location = (0,0)

# Create the variables for the server
server = False
server_ip = ""
server_port = 0

# # Create the variables for the WiFi
# wifi = False
# wifi_ssid = "Mi 10T Pro"
# wifi_password = "teamovida"

# #   Connect to the WiFi
# sta_if = network.WLAN(network.STA_IF)
# if not sta_if.isconnected():
#     print('connecting to network...')
#     sta_if.active(True)
#     sta_if.connect(wifi_ssid, wifi_password)
#     while not sta_if.isconnected():
#         pass
# print('network config:', sta_if.ifconfig())

# Create the variable for the distances
distances = []

# Create the variable for the location
location = (0,0)

# Create the variable for the game
game = False

#   Create the function to clear the board
def ClearBoard():
    distances = sensor_manager.read_distances()
    #   If all the distances are more than 35 cm, then move to the GameDart1 state
    for distance in distances:
        if distance < 35:
            return
    state = State.GameDart1

#   Create the function to detect the first dart
def GameDart1():
    #   Cheack if there is a game
    if game == False:
        return
    #   Read the distances until a dart is detected
    


    

while True:
    # distances = sensor_manager.read_distances()
    # print(distances)
    # time.sleep(1)
    if state == State.NoGame:
        print("No Game")
        if game == False:
            print("No Game")
            #   Ask the server if there is a game
            #   If there is a game, then move to the ClearBoard state
            #   If there is no game, then stay in the NoGame state
        else:
            print("Game")
            #   Ask the server if there is a turn
            #   If there is a turn, then move to the ClearBoard state
            #   If there is no turn, then stay in the NoGame state
    elif state == State.ClearBoard:
        print("Clear Board")
        #   Clear the board
        #   Move to the GameDart1 state
    elif state == State.GameDart1:
        #   Detect the first dart
        #   If the first dart is detected, then move to the GameDart2 state
        #   If the first dart is not detected, then stay in the GameDart1 state
    elif state == State.GameDart2:
        #   Detect the second dart
        #   If the second dart is detected, then move to the GameDart3 state
        #   If the second dart is not detected, then stay in the GameDart2 state
    elif state == State.GameDart3:
        #   Detect the third dart
        #   If the third dart is detected, then move to the NextTurn state
        #   If the third dart is not detected, then stay in the GameDart3 state
    elif state == State.NextTurn:
        #   Ask the server if there is a turn
        #   If there is a turn, then move to the ClearBoard state
        #   If there is no turn, then move to the NoGame state
        




