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
import urequests as requests
import ujson
from neopixel import NeoPixel

# Create the Multiplexer object
mux = Mux(18, 5, 17, 16, 19)

#Setting the NeoPixel
np = NeoPixel(Pin(15), 12)

# Create the sensors objects
sensor0 = UltraSensor(13, 0.5, 19.5, 0.0161, 1.6172) # Pin 13 , location (0,19.8)
sensor1 = UltraSensor(12, 11.6, 15.2, 0.0158, 1.7105) # Pin 12 , location (11.4,16.2)
sensor2 = UltraSensor(14, 18.8, 5.7, 0.016, 1.9421) # Pin 14 , location (18.8,6)
sensor3 = UltraSensor(27, 18.6, -6.2, 0.0158, 2.1619) # Pin 27 , location (18.8,-6)
sensor4 = UltraSensor(26, 11, -16.2, 0.0153, 2.294) # Pin 26 , location (11.4,-16.2)
sensor5 = UltraSensor(25, 0, -19.7, 0.0158, 1.1089) # Pin 25 , location (0,-19.8)
sensor6 = UltraSensor(33, -11.7, -15.9, 0.0164, 1.1967) # Pin 33 , location (-11.4,-16.2)
sensor7 = UltraSensor(32, -18.6, -5.6, 0.0152, 1.8608) # Pin 32 , location (-18.8,-6)
sensor8 = UltraSensor(35, -18.4, 6.6, 0.0154, 1.9196) # Pin 35 , location (-18.8,6)
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
game_id = 0
player_id = 0
game_turn = 0
dart1_location = (0,0)
dart2_location = (0,0)
dart3_location = (0,0)
# Create list of distances, d1Distances, d2Distances
distances = []
d1Distances = []
d2Distances = []
d3Distances = []

# # Create the variables for the WiFi
wifi = False
wifi_ssid = "Mi 10T Pro"
wifi_password = "teamovida"


#   Create a timer
timer = time.ticks_ms()

################################ NeoPixel Functions ################################

#   Function to turn off the NeoPixel
def NeoPixelOff():
    for i in range(12):
        np[i] = (0,0,0)
    np.write()

#   Function to set the neo pixel to green, quarter brightness
def NeoPixelGreen():
    for i in range(12):
        np[i] = (0, 64, 0)
    np.write()

#   Function to set the neo pixel to red, quarter brightness
def NeoPixelRed():
    for i in range(12):
        np[i] = (64, 0, 0)
    np.write()

#   Function to set the neo pixel to blue, quarter brightness
def NeoPixelBlue():
    for i in range(12):
        np[i] = (0, 0, 64)
    np.write()

#   Function to set the neo pixel to orange, quarter brightness
def NeoPixelOrange():
    for i in range(12):
        np[i] = (64, 64, 0)
    np.write()

############################### Testing ########################################
#   Connect to the WiFi
NeoPixelBlue()
sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.active(True)
    sta_if.connect(wifi_ssid, wifi_password)
    while not sta_if.isconnected():
        pass
print('network config:', sta_if.ifconfig())
NeoPixelGreen()

# Make a POST request to the PHP file with X and Y values
x = 10
y = 20
NeoPixelBlue()
url = "https://thor.cnt.sast.ca/~atangari/CMPE2550/Project/esp32Server.php"
data1 = {"x": x, "y": y}
data_json = ujson.dumps(data1)
headers = {"Content-Type": "application/x-www-form-urlencoded"}

response = requests.post(url, data=data_json, headers=headers)
print(response.text)
response.close()

#   Create a post request to the server
data = {"valueX": x, "valueY": y}
#   convert the data to json
data_json1 = ujson.dumps(data)
#   Create the headers
headers = {"Content-Type": "application/json"}
#   Create the request
response = requests.post("https://thor.cnt.sast.ca/~kevenlou/distance/distance.php", data = data_json1, headers = headers)
print(response.text)
response.close()
NeoPixelGreen()

################################ Game Functions ################################

#   Function to check if there is a game
def NoGame():
    global game
    global game_id
    global player_id
    global game_turn
    global url
    #   Request to the server
    data = {"action": "check"}
    #   convert the data to json
    data_json = ujson.dumps(data)
    try:
        response = requests.request("GET", url, data = data_json)
        #   Get the response
        response = response.text
        print(response)
        response.close()
    except:
        print("Error")
    
    #   Check if there is a game
    if game == False:
        return State.NoGame
    #   If there is a game, then move to the ClearBoard state
    return State.ClearBoard

#   Function to clear the board
def ClearBoard():
    global distances
    global dart1_location
    global dart2_location
    global dart3_location
    global d1Distances
    global d2Distances
    global d3Distances
    distances = sensor_manager.read_distances()
    # Set neopixel to orange
    NeoPixelOrange()
    # If all the distances are more than 35 cm, then move to the GameDart1 state
    for distance in distances:
        if distance < 30:
            return State.ClearBoard
    #   Reset the game variables
    dart1_location = (0,0)
    dart2_location = (0,0)
    dart3_location = (0,0)
    d1Distances = []
    d2Distances = []
    d3Distances = []
    return State.GameDart1

#   Function to detect the first dart
def GameDart1():
    #   Global variables
    global distances
    global dart1_location
    global d1Distances
    #   Cheack if there is a game
    if game == False:
        return State.NoGame
    #   Set the timer
    timer = time.ticks_ms()
    #   Set the NeoPixel to green
    NeoPixelGreen()
    #   Read the distances until a dart is detected or 20 seconds have passed
    while time.ticks_diff(time.ticks_ms(), timer) < 20000:        
        #   Read the distances
        distances = sensor_manager.read_distances()
        bullseye = 0
        for distance in distances:
            if distance > 18 and distance < 22:
                bullseye = bullseye + 1
            else:
                bullseye = 0
        #   If the bullseye is detected, then move to the GameDart2 state
        if bullseye == 10:
            #   Set the NeoPixel to red if a dart is detected
            NeoPixelRed()
            dart1_location = (0,0)
            print("Dart 1 Location: " + str(dart1_location))
            d1Distances = distances
            #   Send the dart location to the server
            SendDartLocation(dart1_location)
            return State.GameDart2
        #   If a dart is detected, then move to the GameDart2 state
        for distance in distances:
            if distance < 30:
                #   Set the NeoPixel to red if a dart is detected
                NeoPixelRed()
                #   Read the distances
                distances = sensor_manager.read_distances()
                #   Get the location of the dart
                dart1_location = sensor_manager.get_location()
                print("Dart 1 Location: " + str(dart1_location))
                #   Send the dart location to the server
                SendDartLocation(dart1_location)
                d1Distances = distances
                #   If a dart is detected, then move to the GameDart2 state
                return State.GameDart2
        #   Wait 1 second
        time.sleep(1)
    #   If 20 seconds have passed, then move to the GameDart2 state
    NeoPixelRed()
    dart1_location = (None,None)
    print("Dart 1 Location: " + str(dart1_location))
    #   Send the dart location to the server
    SendDartLocation(dart1_location)
    d1Distances = distances
    return State.GameDart2

#   Function to detect the second dart
def GameDart2():
    #   Global variables
    global distances
    global dart1_location
    global dart2_location
    global d1Distances
    global d2Distances
    #   Cheack if there is a game
    if game == False:
        return State.NoGame
    #   Set the timer
    timer = time.ticks_ms()
    #   Set the NeoPixel to green
    NeoPixelGreen()
    #   Read the distances until a dart is detected or 20 seconds have passed
    while time.ticks_diff(time.ticks_ms(), timer) < 20000:
        distances = sensor_manager.read_distances()
        #   Check if the distances are the same as the first dart
        if (sensor_manager.check_same(d1Distances, distances)):
            continue
        #   Wait 1 second
        time.sleep(1)
        #   Set the NeoPixel to red if a dart is detected
        NeoPixelRed()
        #   Read the distances
        distances = sensor_manager.read_distances()
        #   Get the location of the second dart
        dart2_location = sensor_manager.get_dart_location(d1Distances, distances)
        print("Dart 2 Location: " + str(dart2_location))
        if dart2_location == (None,None):
            continue
        else:            
            #   Send the dart location to the server
            SendDartLocation(dart2_location)
            d2Distances = distances
            return State.GameDart3
        
    #   If 10 seconds have passed, then move to the GameDart3 state
    NeoPixelRed()
    dart2_location = (None,None)
    print("Dart 2 Location: " + str(dart2_location))
    #   Send the dart location to the server
    SendDartLocation(dart2_location)
    d2Distances = distances
    return State.GameDart3

#   Function to detect the third dart
def GameDart3():
    #   Global variables
    global distances
    global dart2_location
    global dart3_location
    global d2Distances

    #   Cheack if there is a game
    if game == False:
        return State.NoGame
    #   Set the timer
    timer = time.ticks_ms()
    #   Set the NeoPixel to green
    NeoPixelGreen()
    #   Read the distances until a dart is detected or 20 seconds have passed
    while time.ticks_diff(time.ticks_ms(), timer) < 20000:
        distances = sensor_manager.read_distances()
        #   Check if the distances are the same as the second dart
        if (sensor_manager.check_same(d2Distances, distances)):
            continue
        #   Wait 1 second
        time.sleep(1)
        #   Set the NeoPixel to red if a dart is detected
        NeoPixelRed()
        #   Read the distances
        distances = sensor_manager.read_distances()
        #   Get the location of the third dart
        dart3_location = sensor_manager.get_dart_location(d2Distances, distances)
        print("Dart 3 Location: " + str(dart3_location))
        if dart3_location == (None,None):
            continue
        else:
            #   Send the dart location to the server
            SendDartLocation(dart3_location)
            return State.NextTurn
        
    #   If 10 seconds have passed, then move to the NextTurn state
    NeoPixelRed()
    dart3_location = (None,None)
    print("Dart 3 Location: " + str(dart3_location))
    #   Send the dart location to the server
    SendDartLocation(dart3_location)
    return State.NextTurn

#   Function to send the dart location to the server
def SendDartLocation( dart_location ):
    #   Global variables
    global game
    global url
    global game_id
    global player_id
    global game_turn
    #   Send the dart location to the server
    data = {"action": "sendDartLocation", 
            # "game_id": game_id, 
            # "player_id": player_id, 
            # "game_turn": game_turn, 
            "dart_locationx": dart_location[0],
            "dart_locationy": dart_location[1]
            }
    data_json = ujson.dumps(data)
    response = requests.post(url, data=data_json)
    response = response.text
    print(response)

#   Function to move to the next turn
def NextTurn():
    #   Global variables
    global game
    global url
    global game_id
    global player_id
    global game_turn
    #   Ask the server if it is the next turn
    #   If it is the next turn, then move to the ClearBoard state
    #   If it is not the next turn, then move to the NoGame state
    data = {"action": "nextTurn"}
    data_json = ujson.dumps(data)
    response = requests.request("GET", url, data=data_json)
    response = response.text
    print(response)

    #   Cheack if there is a game
    if game == False:
        return State.NoGame
    #   Clear the board
    return State.GameDart1

    
    




############################# Main Loop #############################
while True:
    # distances = sensor_manager.read_distances()
    # print(distances)
    # time.sleep(1)
    # time.sleep(1)
    if state == State.NoGame:
        print("No Game")
        state = NoGame()
        if game == False:
            print("No Game")
    #         #   Ask the server if there is a game
    #         #   If there is a game, then move to the ClearBoard state
    #         #   If there is no game, then stay in the NoGame state
        else:
            print("Game")
    #         #   Ask the server if there is a turn
    #         #   If there is a turn, then move to the ClearBoard state
    #         #   If there is no turn, then stay in the NoGame state
    elif state == State.ClearBoard:
        print("Clear Board")
        #   Clear the board
        #   Move to the GameDart1 state
    elif state == State.GameDart1:
        print("Game Dart 1")
        state = GameDart1()
        print(distances)
        print(d1Distances)
        print(dart1_location)
        #   Detect the first dart
        #   If the first dart is detected, then move to the GameDart2 state
        #   If the first dart is not detected, then stay in the GameDart1 state
    elif state == State.GameDart2:
        print("Game Dart 2")
        state = GameDart2()
        print(distances)
        print(d2Distances)
        print(dart2_location)
        #   Detect the second dart
        #   If the second dart is detected, then move to the GameDart3 state
        #   If the second dart is not detected, then stay in the GameDart2 state
    elif state == State.GameDart3:
        print("Game Dart 3")
        state = GameDart3()
        print(distances)
        print(dart3_location)
        #   Detect the third dart
        #   If the third dart is detected, then move to the NextTurn state
        #   If the third dart is not detected, then stay in the GameDart3 state
    elif state == State.NextTurn:
        print("Next Turn")
        state = State.ClearBoard
        #   Ask the server if there is a turn
        #   If there is a turn, then move to the ClearBoard state
        #   If there is no turn, then move to the NoGame state

    time.sleep(1)
        




