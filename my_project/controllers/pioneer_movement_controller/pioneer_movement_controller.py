"""pioneer_movement_controller controller."""

from controller import Robot, GPS, Compass
import math
import time
import struct

CHANNEL = 3

COORDINATE_MATCHING_ACCURACY = 0.01 

THETA_MATCHING_ACCURACY = 1  

MAX_SPEED = 5.24

TANGENSIAL_SPEED = 1.6 #1.345678 #1.6

ROBOT_ANGULAR_SPEED_IN_DEGREES = 300

# create the Robot instance.
robot = Robot()
gps = robot.getDevice('gps')
compass = robot.getDevice('compass')
emitter = robot.getDevice('emitter')
receiver = robot.getDevice('receiver')

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

gps.enable(timestep)
compass.enable(timestep)
receiver.enable(timestep)
receiver.setChannel(CHANNEL)

# fetch motors
left_motor = robot.getDevice('left wheel')
right_motor  = robot.getDevice('right wheel')

left_sensor_names = ['so0', 'so1', 'so2']
right_sensor_names = ['so5', 'so6', 'so7']
left_sensors = []
right_sensors = []
for s in left_sensor_names:
    sen = robot.getDevice(s)
    sen.enable(timestep)
    left_sensors.append(sen)
for s in right_sensor_names:
    sen = robot.getDevice(s)
    sen.enable(timestep)
    right_sensors.append(sen)

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
human_position = [3.16, 3.16, 1]
task_pending = False
state = 'waiting'
count = 0
wait = 0
while True:
    if wait >= 0:
        wait -= 1 
        continue
    queue_len = receiver.getQueueLength()
    if queue_len > 0 and state == 'waiting':
        data = receiver.getBytes() 
        receiver.nextPacket()
        data = struct.unpack("d", data)
        arm = int(data[0])
        emitter.setChannel(arm)
        if arm == 2:
            target_position = [0.8, 0.64, 1.09]
        else:
            target_position = [-0.8, -0.64, 1.09]

        state = 'catching'

    if state == 'catching':
        current_coordinate = gps.getValues()
        if not is_coordinate_equal(current_coordinate, target_position):
            move_to_destination(current_coordinate, target_position)
        else:
            print('destination reached')
            motor_stop()
            d = struct.pack("d", 1)
            emitter.send(d)
            count = 50
            state = 'delivering'

    if state == 'delivering' and count < 0:
        current_coordinate = gps.getValues()
        if not is_coordinate_equal(current_coordinate, human_position):
            move_to_destination(current_coordinate, human_position)
        else:
            print('human reached')
            motor_stop()
            emitter.setChannel(0)
            d = struct.pack("d", 1)
            emitter.send(d)
            state = 'waiting'
    else:
        count -= 1

    step()
    for s in right_sensors:
        val = s.getValue()
        if val > 80:
            motor_rotate_left()
            wait = 200
            continue
    for s in left_sensors:
        val = s.getValue()
        if val > 80:
            motor_rotate_right()
            wait = 200
            continue
    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()

    # Process sensor data here.

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    pass

# Enter here exit cleanup code.
