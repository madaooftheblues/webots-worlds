from controller import Supervisor
import tempfile
import numpy as np

import pinocchio as pin
from pymp import Planner, toSE3

robot = Supervisor()
timeStep = int(4 * robot.getBasicTimeStep())

links_mask = [False, True, True, True, True, True, True] 
# Load the URDF file
# urdf_path = "/home/oathbreaker/Documents/UR5e.urdf"  # Replace with the path to your UR5e URDF file
filename = None
with tempfile.NamedTemporaryFile(suffix='.urdf', delete=False) as file:
    filename = file.name
    file.write(robot.getUrdf().encode('utf-8'))


planner = Planner(
        filename,
        None,
        ee_link_name="wrist_3_link",
        timestep=timeStep,
        joint_vel_limits=1,
        joint_acc_limits=1,
    )

# Get the arm and target nodes.
target = robot.getFromDef('TARGET')

arm = robot.getSelf()

q = [0,0,0, 0]


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

count = 0

init_qpos = np.zeros(17)

# Main loop
while robot.step(64) != -1:
    if count <= 0:
        targetPosition = target.getPosition()
        armPosition = arm.getPosition()
        
        ik_results = planner.compute_CLIK([target, q], init_qpos, max_trials=20, seed=0)
        print("# IK solutions:", len(ik_results))

       # for i, motor in enumerate(motors):
        #    motor.setPosition(ik_results[i+1])
    count += 1        
