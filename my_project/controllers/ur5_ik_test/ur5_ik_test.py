# E. Culurciello 2020

try:
    from ikpy.chain import Chain
    from ikpy.link import Link, OriginLink, URDFLink
except ImportError:
    import sys
    sys.exit('The "ikpy" Python module is not installed. '
             'To run this sample, please upgrade "pip" and install ikpy with this command: "pip install ikpy"')

from controller import Supervisor

# Create the arm chain.
# The constants below have been manually extracted from the UR5e.proto file, looking at the HingeJoint node fields.
# Note the last Link, which defines the hand position / gripper.
armChain = Chain(name='arm', links=[
                OriginLink(),
                URDFLink(
                    name="shoulder_pan_joint",
                    bounds=[-6.28318530718, 6.28318530718], # maxVelocity 3.14, maxTorque 150
                    origin_translation=[0, 0, 0.163],
                    origin_orientation=[0, 0, 0],
                    rotation=[0, 0, 1]
                ),
                URDFLink(
                    name="shoulder_lift_joint",
                    bounds=[-6.28318530718, 6.28318530718], # maxVelocity 3.14, maxTorque 150
                    origin_translation=[0, 0.138, 0],
                    origin_orientation=[0, 0, 0],
                    rotation=[0, 1, 0]
                ),
                URDFLink(
                    name="elbow_joint",
                    bounds=[-3.14159265359, 3.14159265359], # maxVelocity 3.14, maxTorque 150
                    origin_translation=[0, -0.131, 0.425],
                    origin_orientation=[0, 0, 0],
                    rotation=[0, 1, 0]
                ),
                URDFLink(
                    name="wrist_1_joint",
                    bounds=[-6.28318530718, 6.28318530718], # maxVelocity 6.28, maxTorque 28
                    origin_translation=[0, 0, 0.392],
                    origin_orientation=[0, 0, 0],
                    rotation=[0, 1, 0]
                ),
                URDFLink(
                    name="wrist_2_joint",
                    bounds=[-6.28318530718, 6.28318530718], # maxVelocity 6.28, maxTorque 28
                    origin_translation=[0, 0.127, 0],
                    origin_orientation=[0, 0, 0],
                    rotation=[0, 0, 1]
                ),
                URDFLink(
                    name="wrist_3_joint",
                    bounds=[-6.28318530718, 6.28318530718], # maxVelocity 6.28, maxTorque 28
                    origin_translation=[0, 0, 0.1],
                    origin_orientation=[0, 0, 0],
                    rotation=[0, 1, 0]
                ),
                URDFLink(
                    name="gripper",
                    bounds=[0,0],
                    origin_translation=[0.0, 0.1, 0.26],
                    origin_orientation=[0, 0, 0],
                    rotation=[0, 0, 0]
                ),
            ],
    active_links_mask=[False, True, True, True, True, True, False, False]
)

# Initialize the Webots Supervisor.
supervisor = Supervisor()
timeStep = int(4 * supervisor.getBasicTimeStep())

# Initialize the arm motors.
motors = []
for motorName in ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint', 'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']:
    motor = supervisor.getDevice(motorName)
    motor.setVelocity(1.0)
    motors.append(motor)

# Get the arm and target nodes.
obj = supervisor.getFromDef('TARGET')
arm = supervisor.getFromDef('ARM')
obj_pos = obj.getPosition()

print('Move the red box using the mouse...')

while supervisor.step(timeStep) != -1:
    # Get the absolute postion of the target and the arm base.
    objPosition = obj.getPosition()
    armPosition = arm.getPosition()

    # Compute the position of the target relatively to the arm.
    # x and y axis are inverted because the arm is not aligned with the Webots global axes.
    x = objPosition[0] - armPosition[0]
    y = - (objPosition[2] - armPosition[2])
    z = objPosition[1] - armPosition[1]

    ikResults = armChain.inverse_kinematics([x, y, z])

    # actuate motors:
    # for i in range(3):
    for i in range(len(motors)):
        motors[i].setPosition(ikResults[i + 1])

    # Keep the hand origin_orientation down.
    # motors[4].setPosition(-ikResults[2] - ikResults[3] + math.pi / 2)
    # Keep the hand origin_orientation perpendicular.
        motors[5].setPosition(-ikResults[1])
