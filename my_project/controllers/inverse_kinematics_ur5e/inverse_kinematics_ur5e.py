"""inverse_kinematics_ur5e controller."""

from controller import Supervisor
import numpy as np
import tempfile
import ikpy
from ikpy.chain import Chain
from ikpy.link import URDFLink

robot = Supervisor()
timeStep = int(4 * robot.getBasicTimeStep())

state = 'waiting'
speed = 1.0
counter = 90
initial_positions = [0, -1.5, 1.5, 0, 0, 0]
target_positions = [0, -1.88, -2.14, -2.38, -1.51, 0]

map = {
    1: [0, 0, 0, 0, 0, 0],
    2: [0, -0.8, 1.5, -0.8, 0, 0],
    3: [0, -1.0, 2.0, -1.0, 0, 0, 0]
}

# IKPY constants
IKPY_MAX_ITERATIONS = 4

base_elements=["base_link"]
# links_mask = [False, True, True, True, True, True, True, False, True, True, False] 

links_mask = [False, True, True, True, True, True, True, False, False, True, False] 
# Load the URDF file
# urdf_path = "/home/oathbreaker/Documents/UR5e.urdf"  # Replace with the path to your UR5e URDF file

filename = None
with tempfile.NamedTemporaryFile(suffix='.urdf', delete=False) as file:
    filename = file.name
    file.write(robot.getUrdf().encode('utf-8'))
my_chain = Chain.from_urdf_file(filename, base_elements=base_elements, active_links_mask= links_mask)


# Get the arm and target nodes.
target = robot.getFromDef('CAN')

arm = robot.getSelf()

# Get arm motors
arm_motor_names = ["shoulder_pan_joint","shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"]
arm_motors = [robot.getDevice(name) for name in arm_motor_names]

for motor in arm_motors:
        motor.setVelocity(1)
        position_sensor = motor.getPositionSensor()
        position_sensor.enable(timeStep)

hand_motor_names = ["finger_middle_joint_1","finger_1_joint_1","finger_2_joint_1"]
hand_motors = [robot.getDevice(name) for name in hand_motor_names]

# Get hand motors
for motor in hand_motors:
        motor.setVelocity(1)
        position_sensor = motor.getPositionSensor()
        position_sensor.enable(timeStep)

# List of all motors
motors = arm_motors + hand_motors

# function definitions
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

def inv_kin(arm_position, target_position):
        # Compute the position of the target relatively to the arm.
        # x and y axis are inverted because the arm is not aligned with the Webots global axes.
        x = -(target_position[1] - arm_position[1])
        y = target_position[0] - arm_position[0]
        z = target_position[2] - arm_position[2]
        
        # Call "ikpy" to compute the inverse kinematics of the arm.
        initial_position = [0] + [m.getPositionSensor().getValue() for m in arm_motors] + [0] + [m.getPositionSensor().getValue() for m in hand_motors]
        # print(initial_position)
        ik_results = my_chain.inverse_kinematics([x, y, z], initial_position=initial_position, max_iter= 40)
        # angles = my_chain.inverse_kinematics(target_position)
        print(ik_results)
        
        return ik_results 

def set_angles(angles):
    for i, motor in enumerate(motors):
        if i == 5: continue
        motor.setPosition(angles[i])        
        
reset_arm_pos()

# Main loop
while robot.step(64) != -1:
    if counter <= 0:
        if state == 'testing':
            arm_motors[1].setPosition(-1.1)
            arm_motors[2].setPosition(2)
            arm_motors[3].setPosition(-0.8)
        elif state == 'waiting':
            target_pos = target.getPosition()
            arm_pos = arm.getPosition()
            angles = inv_kin(arm_pos, target_pos)
            angles = np.delete(angles,(0,7))
            print(angles)
            set_angles(angles)
            counter = 120
            state = 'grasping'
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