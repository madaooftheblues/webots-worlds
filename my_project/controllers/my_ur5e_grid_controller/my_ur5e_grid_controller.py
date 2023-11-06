"""my_ur5e_grid_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot

# Define constants
TIME_STEP = 32

# create the Robot instance.
robot = Robot()

state = 'WAITING'
speed = 1.0
counter = 0

target_positions = [-1.88, -2.14, -2.38, -1.51]


# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)

# Get motors and sensors
motor_names = ["shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint"]
arm_motors = [robot.getDevice(name) for name in motor_names]

hand_motor_names = ["finger_middle_joint_1","finger_1_joint_1","finger_2_joint_1"]
hand_motors = [robot.getDevice(name) for name in hand_motor_names]

for motor in arm_motors:
    motor.setVelocity(speed)

distance_sensor = robot.getDevice("distance sensor")
distance_sensor.enable(TIME_STEP)

position_sensor = robot.getDevice("wrist_1_joint_sensor")
position_sensor.enable(TIME_STEP)

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(TIME_STEP) != -1:    
    if counter <= 0:
        match state:
            case 'WAITING':
                if distance_sensor.getValue() < 500 :
                    state = 'GRASPING'
                    counter = 8
                    print("Grasping can")
                    print(counter)
                    for motor in hand_motors:
                        motor.setPosition(0.85)
                break
            case 'GRASPING':
                for i in range(4):
                    arm_motors[i].setPosition(target_positions[i])
                print("Rotating arm")
                state = 'ROTATING'
                break
            case 'ROTATING':
                if position_sensor.getValue() < -2.3 :
                    counter = 8
                    print("Releasing can")
                    state = 'RELEASING'
                    for motor in hand_motors:
                        motor.setPosition(motor.getMinPosition())
                break
            case 'RELEASING':
                for motor in arm_motors:
                    motor.setPosition(0.0)
                print("Rotating arm back")
                state = 'ROTATING_BACK';
                break
            case 'ROTATING_BACK':
                if position_sensor.getValue() > -0.1 :
                    state = 'WAITING'
                    print("Waiting can")
                break
            case _:
                print(state)
    counter -= 1
    pass

print('sds')
# Enter here exit cleanup code.
