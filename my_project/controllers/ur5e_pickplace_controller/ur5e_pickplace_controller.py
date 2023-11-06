"""ur5e_pickplace_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
# Import necessary Webots modules
from controller import Robot, Supervisor

# Initialize the robot
robot = Supervisor()

motors = []
motors.append(robot.getDevice("elbow_joint"))
motors.append(robot.getDevice("shoulder_pan_joint"))
motors.append(robot.getDevice("shoulder_lift_joint"))
motors.append(robot.getDevice("wrist_1_joint"))
motors.append(robot.getDevice("wrist_2_joint"))
motors.append(robot.getDevice("wrist_3_joint"))


for motor in motors:
        motor.setVelocity(0.5)

# Define the UR5e arm motors (you should update these names accordingly)
arm_motors = [robot.getDevice("shoulder_pan_joint"), robot.getDevice("shoulder_lift_joint")]

# Define the gripper motor (you should update this name accordingly)
gripper_motor = robot.getDevice("finger_middle_joint_1")

# Define object positions (change these values according to your environment)
target = robot.getFromDef('TARGET')
pickup_position = target.getPosition()  # Example pickup position
placement_position = [0.5, 0.4, 0.5]  # Example placement position

# Define control parameters
pickup_height = 0.03  # Height above the object for pickup
gripper_opening_angle = 0.0495  # Maximum allowed angle for gripper opening
gripper_closing_angle = 0.0  # Angle to close the gripper

# Function to move the arm to a specific position
def move_arm_to_position(position):
    for i, motor in enumerate(motors):
        motor.setPosition(position[i])

# Function to control the gripper while clamping the position
def control_gripper_with_clamp(desired_position):
    min_position = gripper_motor.getMinPosition()
    max_position = gripper_motor.getMaxPosition()
    clamped_position = max(min(desired_position, max_position), min_position)
    gripper_motor.setPosition(clamped_position)

# Main control loop
while robot.step(64) != -1:
    # Move the arm to the pickup position
    for motor in motors:
        motor.setPosition(9)    
    # Lower the gripper to the pickup height
    
    # Open the gripper (clamped to valid range)
    control_gripper_with_clamp(gripper_opening_angle)
    
    # Close the gripper after a delay (simulating object pickup)
    robot.step(100)
    control_gripper_with_clamp(gripper_closing_angle)
    
    # Move the arm to the placement position
    
    # Release the gripper (open) at the placement position
    control_gripper_with_clamp(gripper_opening_angle)
    
    # Move the arm back to the initial position for the next iteration
