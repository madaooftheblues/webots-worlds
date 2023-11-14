"""supervisor_cam_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Supervisor, Node, Camera
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import struct
import math

# create the Robot instance.
robot = Supervisor()
emitter = robot.getDevice('emitter')
object = "SoccerBall"
radius = 0.054
# Get the time step of the current world (simulation)
time_step = int(robot.getBasicTimeStep())
object_coords = {
    "Orange": [0.12, -0.12, 0.79],
    "Wineglass": [-0.12, 0.37, 0.79],
    "Apple": [0.37, 0.12, 0.79],
    "RubberDuck": [-0.12, 0.12, 0.79],
    "SoccerBall": [0.37, 0.37, 0.81]
}

object_poses = {
    "Orange": (1,1),
    "Wineglass": (0,1),
    "Apple": (1,3),
    "RubberDuck": (1,1),
    "SoccerBall": (0,3)
}

# Spawn object
root_node = robot.getRoot()
root_children = root_node.getField('children')
root_children.importMFNodeFromString(-1, f'{object}{{ translation {object_coords[object][0]} {object_coords[object][1]} {object_coords[object][2]} }}')

# Configure soccerball radius
if object == 'SoccerBall':
    # Get the root node of the scene
    root_children = root_node.getField('children')
    num_of_nodes = root_children.getCount()
    soccer_node = None
    for i in range(num_of_nodes):
        node = root_children.getMFNode(i)
        name = node.getTypeName()
        print(name)
        if name == "SoccerBall":
            soccer_node = node
            break;
    soccer_node.getField("radius").setSFFloat(radius)
       
# Distance calculator
def measure_dist(p1, p2):
    return math.dist(p1,p2)

# Choose which robot arm is to pick
def choose_robot():
    arm_1 = robot.getFromDef('ARM1')
    arm_2 = robot.getFromDef('ARM2')
    
    arm_1_coords = arm_1.getPosition()
    arm_2_coords = arm_2.getPosition()
    dist_1 = measure_dist(object_coords[object], arm_1_coords)
    dist_2 = measure_dist(object_coords[object], arm_2_coords)
    
    if dist_1 <= dist_2: return 1
    return 2

# Set emitter channel
emitter.setChannel(choose_robot())
message = struct.pack("dd",object_poses[object][0], object_poses[object][1])
emitter.send(message)
"""
def get_world_info():
    # Get the root node of the scene
    root_node = robot.getRoot()
    root_children = root_node.getField('children')
    num_of_nodes = root_children.getCount()
    print(num_of_nodes)
    robot_nodes = []
    for i in range(num_of_nodes):
        node = root_children.getMFNode(i)
        type = node.getType()
        name = node.getTypeName()
        print(name, type)
        if type == Node.ROBOT:
            print(node.getPosition())
            robot_nodes.append(name)
    print(robot_nodes) 
    # return {"robots": robots, "objects": objects}

# Create a FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/webots/play")
async def play_simulation():
    robot.simulationSetMode(robot.SIMULATION_MODE_FAST)
    robot.step(time_step)
    return {"message" : "Simulation started"}
@app.post("/webots/pause")
async def pause_simulation():
    robot.simulationSetMode(robot.SIMULATION_MODE_PAUSE)
    robot.step(0)
    return {"message" : "Simulation stopped"}

# Function to start the FastAPI server
def start_fastapi_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Start the FastAPI server in a separate thread
fastapi_server_thread = threading.Thread(target=start_fastapi_server)
fastapi_server_thread.start()
"""

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)
camera = robot.getDevice("camera")
camera.enable(time_step)
# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(time_step) != -1:

    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()

    # Process sensor data here.

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    pass

# Enter here exit cleanup code.
