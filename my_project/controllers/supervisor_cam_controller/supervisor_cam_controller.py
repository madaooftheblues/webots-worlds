"""supervisor_cam_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Supervisor, Node, Camera
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
import struct
import math
from control import Control 
from task import TaskManager, PickPlace 
from world import Artifact, Grid

# message from frontend 
class Message_(BaseModel):
    message: str

class Message:
    def __init__(self):
        self.message = ''
    def set_message(self, message: str):
        self.message = message
    def get_message(self):
        return self.message

m = Message()

# task prototype
class Task_(BaseModel):
    title: str
    operation: str
    
# simulation controls
control = Control()

# task manager
task_manager = TaskManager()

# create the Robot instance.
robot = Supervisor()
emitter = robot.getDevice('emitter')
# Get the time step of the current world (simulation)
time_step = int(robot.getBasicTimeStep())

grid = Grid()

grid.add_artifact( Artifact("Orange", [0.12, -0.12, 0.79], (1, 1)) )
grid.add_artifact( Artifact("Wineglass", [-0.12, 0.37, 0.79], (0, 1)) )
grid.add_artifact( Artifact("Apple", [0.37, 0.12, 0.79], (1, 3)) )
grid.add_artifact( Artifact("RubberDuck", [-0.12, 0.12, 0.79], (1, 1)) )
grid.add_artifact( Artifact("SoccerBall", [0.37, 0.37, 0.81], (0, 3)) )

grid.print_artifacts()

# Spawn object
root_node = robot.getRoot()
root_children = root_node.getField('children')

artifacts = grid.get_artifacts()

for art in artifacts:
    name = art.get_name()
    coord = art.get_coord()

    root_children.importMFNodeFromString(-1, f'{name}{{ translation {coord[0]} {coord[1]} {coord[2]} }}')

    # Configure soccerball radius
    if name  == 'SoccerBall':
        num_of_nodes = root_children.getCount()
        soccer_node = None
        radius = 0.054
        for i in range(num_of_nodes):
            node = root_children.getMFNode(i)
            name = node.getTypeName()
            print(name)
            if name == "SoccerBall":
                soccer_node = node
                break;
        soccer_node.getField("radius").setSFFloat(radius)
    

# pick and place task function
def pick_place(target:str):

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
    coordinates = struct.pack("dd", object_poses[target][0], object_poses[target][1])
    emitter.send(coordinates)


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
"""

# Create a FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_URL = "0.0.0.0"
PORT = 8000
base_route = '/webots/'

@app.post(base_route)
async def receive_message(m_obj: Message_):
    m.set_message(m_obj.message)
    return {"message" : m_obj.message}

@app.post(base_route + 'control')
async def receive_control(c_obj: Message_):
    control.set_mode(c_obj.message)
    return {"message" : c_obj.message}

@app.post(base_route + 'task')
async def receive_task(t_obj: Task_):
    op = t_object.operation

    match op:
        case 'PickPlace':
            t = PickPlace(t_obj.title, t_obj.operation, t_obj.target)
            task_manager.addTask(t)

    return {"message" : t_obj.message}

# Function to start the FastAPI server
def start_fastapi_server():
    uvicorn.run(app, host = API_URL, port = PORT)

# Start the FastAPI server in a separate thread
fastapi_server_thread = threading.Thread(target=start_fastapi_server)
fastapi_server_thread.start()

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)
camera = robot.getDevice("camera")
camera.enable(time_step)

# Main loop:
if __name__ == '__main__':
    while True:
        control.monitor(robot, time_step)
        
# Enter here exit cleanup code.
