"""pioneer_movement_controller controller."""

from controller import Robot, GPS, Compass
import math
import time

COORDINATE_MATCHING_ACCURACY = 0.01 

THETA_MATCHING_ACCURACY = 1  

MAX_SPEED = 5.24

TANGENSIAL_SPEED = 1.345678 #1.6

ROBOT_ANGULAR_SPEED_IN_DEGREES = 300

# create the Robot instance.
robot = Robot()
gps = robot.getDevice('gps')
compass = robot.getDevice('compass')

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

gps.enable(timestep)
compass.enable(timestep)

# fetch motors
left_motor = robot.getDevice('left wheel')
right_motor  = robot.getDevice('right wheel')

# set motors
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))

left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)
target_position = [-0.8, -0.64, 1.09]

def motor_stop():
    left_motor.setVelocity(0.0);
    right_motor.setVelocity(0.0);

def motor_move_forward():
    left_motor.setVelocity(MAX_SPEED);
    right_motor.setVelocity(MAX_SPEED);

def motor_rotate_left():
    left_motor.setVelocity(-MAX_SPEED);
    right_motor.setVelocity(MAX_SPEED);

def motor_rotate_right():
    left_motor.setVelocity(MAX_SPEED);
    right_motor.setVelocity(-MAX_SPEED);

def get_robot_bearing():
    north = compass.getValues()
    rad = math.atan2(north[0], north[2])
    bearing = (rad - 1.5708) / math.pi * 180.0
    if bearing < 0.0:
        bearing += 360.0
    return bearing

def robot_bearing_to_heading(heading):
    h = 360 - heading

    h = h + 90
    if h > 360.0:
        h = h - 360.0

    return h

def get_robot_heading():
    return robot_bearing_to_heading( get_robot_bearing() )


def is_coordinate_equal(coordinate1, coordinate2):
    if (
        abs(coordinate1[0] - coordinate2[0]) < COORDINATE_MATCHING_ACCURACY
        and abs(coordinate1[1] - coordinate2[1]) < COORDINATE_MATCHING_ACCURACY
    ):
        return True
    else:
        return False

def is_theta_equal(theta, theta2):
    if abs(theta - theta2) < THETA_MATCHING_ACCURACY:
        return True
    else:
        return False

def destination_theta_in_degrees(current_coordinate, destination_coordinate):
    return (
        math.atan2(
            destination_coordinate[1] - current_coordinate[1],
            destination_coordinate[0] - current_coordinate[0],
        )
        * 180
        / math.pi
    )

def cal_theta_dot(heading, destination_theta):
    theta_dot = destination_theta - heading

    if theta_dot > 180:
        theta_dot = -(360 - theta_dot)
    elif theta_dot < -180:
        theta_dot = 360 + theta_dot

    return theta_dot

def cal_theta_dot_to_destination(destination_coords):
    current_coords = gps.getValues()
    robot_heading = get_robot_heading()
    destination_theta = destination_theta_in_degrees(current_coords, destination_coords)
    return cal_theta_dot(robot_heading, destination_theta)

def step():
    robot.step(timestep)

def rotate_heading(theta_dot):
    if not is_theta_equal(theta_dot, 0):
        duration = abs(theta_dot) / ROBOT_ANGULAR_SPEED_IN_DEGREES
        print('theta', theta_dot)
        print('duration', duration)
        if theta_dot > 0:
            motor_rotate_left()
        elif theta_dot < 0:
            motor_rotate_right()
        start_time = robot.getTime()
        while robot.getTime() < start_time + duration:
            step()

def cal_distance(current_coordinate, destination_coordinate):
    return math.sqrt(
        pow(destination_coordinate[0] - current_coordinate[0], 2)
        + pow(destination_coordinate[1] - current_coordinate[1], 2)
    )

def cal_distance_to_destination(destination_coordinate):
    current_coordinate = gps.getValues()
    return cal_distance(current_coordinate, destination_coordinate)

def move_forward(distance):
    duration = distance / TANGENSIAL_SPEED
    print(duration)
    motor_move_forward()
    start_time = robot.getTime()
    while robot.getTime() < start_time + duration:
        step()
    motor_stop()
    step()

def move_to_destination(current_coordinate, destination_coordinate):
    theta_dot_to_destination = cal_theta_dot_to_destination(destination_coordinate)
    rotate_heading(theta_dot_to_destination)
    distance_to_destination = cal_distance_to_destination(destination_coordinate)
    move_forward(distance_to_destination)
    current_coordinate = gps.getValues()

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while True:
    current_coordinate = gps.getValues()
    if not is_coordinate_equal(current_coordinate, target_position):
        move_to_destination(current_coordinate, target_position)
    else:
        print('hhe')
        motor_stop()
        step()
    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()

    # Process sensor data here.

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    pass

# Enter here exit cleanup code.
