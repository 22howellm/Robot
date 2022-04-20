#This is where your main robot code resides. It extendeds from the BrickPi Interface File
#It includes all the code inside brickpiinterface. The CurrentCommand and CurrentRoutine are important because they can keep track of robot functions and commands. Remember Flask is using Threading (e.g. more than once process which can confuse the robot)
from interfaces.brickpiinterface import *
import global_vars as GLOBALS
import logging

class Robot(BrickPiInterface):
    
    def __init__(self, timelimit=10, logger=logging.getLogger()):
        super().__init__(timelimit, logger)
        self.CurrentCommand = "stop" #use this to stop or start functions
        self.CurrentRoutine = "stop" #use this stop or start routines
        return
        
        
    #Create a function to move time and power which will stop if colour is detected or wall has been found
    def move_forward_check(self, power = 20, move_dist = 42, deviation = 1.9):
        reverse = False
        start_time = time.time()
        init_dist = self.get_ultra_sensor()
        bp = self.BP
        while (init_dist - self.get_ultra_sensor() < move_dist):
            bp.set_motor_power(self.rightmotor, power)
            bp.set_motor_power(self.leftmotor, power + deviation)
        return
    
    def turn90_robot(self):
        self.rotate_power_degrees_IMU(10,90,-0.6)
        return

    #Create a function to search for victim

    
    
    #Create a routine that will effective search the maze and keep track of where the robot has been.
    def automatic_search(self):
        self.CurrentRoutine = "automated search"
        th_heading = 0
        opposite = {0:180,180:0,90:270,270:90}
        currenttile = 0
        data = {}
        known_area = {}
        immediate_area = {0:None,90:None,180:None,270:None}
        self.turn90_robot()
        while self.CurrentRoutine == "automated search":
            print("GOT HERE")
            openings = 0
            if th_heading != 0:
                while th_heading != 0:
                    self.turn90_robot()
                    th_heading += 90
                    if th_heading >= 360:
                        th_heading = 0
            for i in immediate_area:
                print('working2')
                distance = self.get_ultra_sensor()
                if distance > 42:
                    #if it detects a something between and 42 cm in front of it its assumes it is a wall
                    if immediate_area[i] == None:
                        immediate_area[i] = 'unexplored'
                    elif immediate_area[i] == 'completely_explored':
                        openings -= 1 
                    else:
                        pass
                    openings += 1
                else:
                    immediate_area[i] = 'walled'
                    #search for image, search if there is a wall so it only helps a victim if it is near.
                self.turn90_robot()
                th_heading += 90
                if th_heading >= 360:
                    th_heading = 0
            if openings > 1:
                known_area[currenttile] = ('completely_explored')
            else:
                known_area[currenttile] = ('partly_explored')
            for i in immediate_area:
                if immediate_area[i] == "walled":
                    pass
                elif immediate_area[i] == 'unexplored':
                    self.move_forward_check()
                    currenttile += 1
                else:
                    currenttile = immediate_area[i]
                    immediate_area = known_area[currenttile]
                    self.move_forward_check()
                    break
                self.turn90_robot()
                th_heading += 90
                if th_heading >= 360:
                    th_heading = 0
            break
        return



# Only execute if this is the main file, good for testing code
if __name__ == '__main__':
    logging.basicConfig(filename='logs/robot.log', level=logging.INFO)
    ROBOT = Robot(timelimit=5)  #10 second timelimit before
    bp = ROBOT.BP
    ROBOT.configure_sensors() #This takes 4 seconds
    start = time.time()
    limit = start + 10
    input("Press Enter to test")
    while (time.time() < limit):
        ROBOT.automatic_search()
    sensordict = ROBOT.get_all_sensors()
    ROBOT.safe_exit()