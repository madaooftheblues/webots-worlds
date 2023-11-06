from controller import Supervisor
import numpy as np
import tempfile
import ikpy
from ikpy.chain import Chain
from ikpy.link import URDFLink

robot = Supervisor()
timeStep = int(4 * robot.getBasicTimeStep())

IKPY_MAX_ITERATIONS = 4

base_elements=["base_link"]
links_mask = [False, True, True, True, True, True, True, False, False, True, False] 
# Load the URDF file
# urdf_path = "/home/oathbreaker/Documents/UR5e.urdf"  # Replace with the path to your UR5e URDF file

filename = None
with tempfile.NamedTemporaryFile(suffix='.urdf', delete=False) as file:
    filename = file.name
    file.write(robot.getUrdf().encode('utf-8'))
my_chain = Chain.from_urdf_file(filename, base_elements=base_elements, active_links_mask= links_mask)


# Get the arm and target nodes.
target = robot.getFromDef('TARGET')

arm = robot.getSelf()

#Get motors
motors = []
motors.append(robot.getDevice('shoulder_pan_joint'))
motors.append(robot.getDevice('shoulder_lift_joint'))
motors.append(robot.getDevice('elbow_joint'))

motors.append(robot.getDevice('wrist_1_joint'))
motors.append(robot.getDevice('wrist_2_joint'))
motors.append(robot.getDevice('wrist_3_joint'))

for motor in motors:
        motor.setVelocity(0.5)
        position_sensor = motor.getPositionSensor()
        position_sensor.enable(timeStep)

hand_motor_names = ["finger_middle_joint_1","finger_1_joint_1","finger_2_joint_1"]
hand_motors = [robot.getDevice(name) for name in hand_motor_names]

for motor in hand_motors:
        motor.setVelocity(0.5)
        position_sensor = motor.getPositionSensor()
        position_sensor.enable(timeStep)


motors[1].setPosition(-1.5)
motors[2].setPosition(1.5)

count = 90

# Main loop
while robot.step(64) != -1:
    if count <= 0:
        targetPosition = target.getPosition()
        armPosition = arm.getPosition()
        
        # Compute the position of the target relatively to the arm.
        # x and y axis are inverted because the arm is not aligned with the Webots global axes.
        x = -(targetPosition[1] - armPosition[1])
        y = targetPosition[0] - armPosition[0]
        z = targetPosition[2] - armPosition[2]
        
        # Call "ikpy" to compute the inverse kinematics of the arm.
        initial_position = [0] + [m.getPositionSensor().getValue() for m in motors] + [0] + [m.getPositionSensor().getValue() for m in hand_motors]
        print(initial_position)
        ikResults = my_chain.inverse_kinematics([x, y, z], initial_position=initial_position)
        
        # angles = my_chain.inverse_kinematics(target_position)
        print(ikResults)
        
        for i, motor in enumerate(motors):
            motor.setPosition(ikResults[i+1])
    count -= 1        