#This is where your main robot code resides. It extendeds from the BrickPi Interface File
#It includes all the code inside brickpiinterface. The CurrentCommand and CurrentRoutine are important because they can keep track of robot functions and commands. Remember Flask is using Threading (e.g. more than once process which can confuse the robot)
from interfaces.brickpiinterface import *
import global_vars as GLOBALS
from numpy import append
import numpy as np
import logging

class Robot(BrickPiInterface):
    
    def __init__(self, timelimit=10, logger=logging.getLogger()):
        super().__init__(timelimit, logger)
        self.CurrentCommand = "stop" #use this to stop or start functions
        self.CurrentRoutine = "stop" #use this stop or start routines
        return
        
        
    #Create a function to move time and power which will stop if colour is detected or wall has been found
    def move_forward_check(self,distanceCm,speed=100,power=100):
        distance = distanceCm * 360 / (np.pi * 5.6)
        BP = self.BP
        try:
            BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A)) # reset encoder A
            BP.offset_motor_encoder(BP.PORT_D, BP.get_motor_encoder(BP.PORT_D)) # reset encoder D
            BP.set_motor_limits(BP.PORT_A, power, speed)    # float motor D
            BP.set_motor_limits(BP.PORT_D, power, speed)          # optionally set a power limit (in percent) and a speed limit (in Degrees Per Second)
            while True:
                BP.set_motor_position(BP.PORT_D, distance+10)    # set motor A's target position to the current position of motor D
                BP.set_motor_position(BP.PORT_A, distance+10)
                time.sleep(0.02)
                if BP.get_motor_encoder(BP.PORT_D) >= distance or BP.get_motor_encoder(BP.PORT_A) >= distance:
                    break
                #print("A:  " + str(distance+10) + "   " + str(BP.get_motor_encoder(BP.PORT_A)))
                #print("D:  " + str(distance+10) + "   " + str(BP.get_motor_encoder(BP.PORT_D)))
        except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
            BP.reset_all()
        return 
    def turn90_robot(self):
        self.rotate_power_degrees_IMU(10,90,1.9) #-0.6
        return 

    #Create a function to search for victim
    
    #Create a routine that will effective search the maze and keep track of where the robot has been.
    def automatic_search(self):
        self.CurrentRoutine = "automated search"
        th_heading = 0
        opposite = {0:180,180:0,90:270,270:90}
        direction_support_x = {0:1,180:-1}
        direction_support_y = {270:-1,90:1}
        currenttile = 0
        currenttile_x = 0
        currenttile_y = 0
        data = {}
        known_area = {}
        known_area_information = {}
        area_location = {}
        immediate_area = {0:None,90:None,180:None,270:None}
        while self.CurrentRoutine == "automated search":
            print("GOT HERE")
            openings = 0
            if th_heading != 0:
                while th_heading != 0:
                    self.turn90_robot()
                    th_heading += 90
                    if th_heading >= 360:
                        th_heading = 0
            for direction in immediate_area:
                print('working2')
                distance = self.get_ultra_sensor()
                if distance > 27:
                    #if it detects a something between and 42 cm in front of it its assumes it is a wall
                    if immediate_area[direction] == None:
                        known_tile = None
                        if direction == 0 or direction == 180:
                            temp_tile = (str(currenttile_x + direction_support_x[direction]) + "," + str(currenttile_y))
                            for i in known_area:
                                if known_area[i] == temp_tile:
                                    known_tile = temp_tile
                        elif direction == 90 or direction == 270:
                            temp_tile = (str(currenttile_x) + "," + str(currenttile_y + direction_support_y[direction]))
                            for i in known_area[i]:
                                if known_area[i] == temp_tile:
                                    known_tile = temp_tile
                        else: 
                            immediate_area[direction] = 'unexplored'
                        if known_tile:
                            immediate_area[direction] = known_tile                        
                    elif immediate_area[direction] == 'completely_explored':
                        openings -= 1 
                        # fix this area

                        broken
                    else:
                        pass
                    openings += 1
                else:
                    immediate_area[direction] = 'walled'
                    #search for image, search if there is a wall so it only helps a victim if it is near.
                self.turn90_robot()
                th_heading += 90
                if th_heading >= 360:
                    th_heading = 0
            if openings > 1:
                known_area[currenttile] = ('completely_explored')
            else:
                known_area[currenttile] = ('partly_explored')
            area_location[currenttile] = (str(currenttile_x) + "," + str(currenttile_y))
            for direction in immediate_area:
                if navigate == False:
                    if immediate_area[direction] == "walled":
                        pass
                    elif immediate_area[direction] == 'unexplored':
                        self.move_forward_check(42)
                        currenttile += 1
                        """if th_heading == 0 or th_heading == 180:
                            currenttile +=
                        elif

                        elif

                        elif
                        navigate = True"""
                    else:
                        currenttile = immediate_area[i]
                        immediate_area = known_area[currenttile]
                        self.move_forward_check(42)
                        navigate = True
                    if navigate == False:
                        self.turn90_robot()
                        th_heading += 90
                        if th_heading >= 360:
                            th_heading = 0
        return
# Only execute if this is the main file, good for testing code
if __name__ == '__main__':
    logging.basicConfig(filename='logs/robot.log', level=logging.INFO)
    ROBOT = Robot(timelimit=5)  #10 second timelimit before
    bp = ROBOT.BP
    ROBOT.configure_sensors() #This takes 4 seconds
    bp.CurrentRoutine = 'stop'
    start = time.time()
    limit = start + 10
    #input("Press Enter to test")
    while True:
        ROBOT.automatic_search()
    sensordict = ROBOT.get_all_sensors()
    ROBOT.safe_exit()