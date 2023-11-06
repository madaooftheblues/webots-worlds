from controller import Supervisor
import numpy as np
import pyikfastur5e

robot = Supervisor()
timeStep = int(4 * robot.getBasicTimeStep())

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

count = 0

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

        ikResults = pyikfastur5e.inverse(target_position, [0,0,0,0,1,0])
        
        # angles = my_chain.inverse_kinematics(target_position)
        print(ikResults)
        
        for i, motor in enumerate(motors):
            motor.setPosition(ikResults[i+1])
    count += 1      