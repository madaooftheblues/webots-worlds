"""death_warrant controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot

# create the Robot instance.
robot = Robot()

state = 'waiting'
speed = 1.0
counter = 90
# initial_positions = [0, -1.5, 1.5, 0, 0, 0]
initial_positions = [1.3, -2.2, 2.0, -1.4, -1.6, 1.3]
target_positions = [0, -1.88, -2.14, -2.38, -1.51, 0]

# map = {
#    1: [0, 0, 0, 0, 0, 0],
#    2: [0, -0.8, 1.5, -0.8, 0, 0],
#    3: [0, -1.0, 2.0, -1.0, 0, 0, 0]
#}


grid = {
    # (0,0): [0.55, -1.2, 1.8, -2, -1.58825, 1.32645],
    (0,0): [0.55, -1.2, 1.9, -2.2, -1.58, 1.32],
    # (0,1): [0.9, -1.0, 2.15, -2.2, -1.58, 1.32],
    (0,1): [0.95, -1.55, 2.185, -2.1, -1.6, 1.9],
    (0,2): [1.55, -1.55, 2.185, -2.1, -1.6, 1.9],
    # (0,2): [1.6, -1.0, 2.15, -2.2, -1.58, 1.32],
    (0,3): [2.1, -1.2, 1.9, -2.2, -1.58, 1.32],
    (1,0): [0.85, -0.8, 1.3, -2.0, -1.58, 1.32],
    (1,1): [1.2, -1.0, 1.5, -2.0, -1.58, 1.32],
    (1,2): [1.55, -1.0, 1.5, -2.0, -1.58, 1.32],
    (1,3): [1.9, -0.8, 1.3, -2.0, -1.58, 1.32],
}

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)

# Get motors and sensors
motor_names = ["shoulder_pan_joint","shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"]
arm_motors = [robot.getDevice(name) for name in motor_names]

hand_motor_names = ["finger_middle_joint_1","finger_1_joint_1","finger_2_joint_1"]
hand_motors = [robot.getDevice(name) for name in hand_motor_names]

for motor in arm_motors:
    motor.setVelocity(speed)

for motor in hand_motors:
    motor.setVelocity(speed)

distance_sensor = robot.getDevice("distance sensor")
distance_sensor.enable(timestep)

position_sensor = robot.getDevice("wrist_1_joint_sensor")
position_sensor.enable(timestep)

def set_arm_pos(pos):
    for i, motor in enumerate(arm_motors):
        motor.setPosition(pos[i])

def reset_arm_pos():
    for i, motor in enumerate(arm_motors):
        motor.setPosition(initial_positions[i])

def grasp():
    for motor in hand_motors:
        motor.setPosition(0.85)
        
def release():
    for motor in hand_motors:
        motor.setPosition(motor.getMinPosition())

reset_arm_pos()
x = 0
y = 0
# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    if counter <= 0:
        if state == 'testing':
            pos = [0.95, -1.55, 2.185, -2.1, -1.6, 1.9]
            set_arm_pos(pos)
        elif state == 'waiting':
            set_arm_pos(grid[(y,x)])
            counter = 90
            state = 'grasping'
            if x < 3: x += 1
            else:
                x = 0
                y = 1
        elif state == 'grasping': 
            grasp()
            counter = 90
            state = 'rotating'
        elif state == 'rotating':
                set_arm_pos(target_positions)
                counter = 120
                state = 'releasing'
        elif state == 'releasing':
                release()
                state = 'reset'
        elif state == 'reset':
                reset_arm_pos()
                counter = 120
                state = 'waiting'
    counter -= 1  
    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()

    # Process sensor data here.

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    pass

# Enter here exit cleanup code.
