"""supervisor_cam_controller controller."""

from controller import Supervisor, Node, Camera
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
from control import Control 
from task import Task, TaskManager, PickPlace 
from world import Artifact, Grid, World
import uuid
import struct

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

# robot prototype
class Robot_(BaseModel):
    id: str
    name: str
    position: list

# task prototype
class Task_(BaseModel):
    id: str
    name: str
    operation: str
    target: str
    
# simulation controls
control = Control()

# task manager
task_manager = TaskManager()

# task pending?
task_pending = False

# create the Robot instance.
robot = Supervisor()
emitter = robot.getDevice('emitter')
receiver = robot.getDevice('receiver')
# get the time step of the current world (simulation)
time_step = int(robot.getBasicTimeStep())

receiver.enable(time_step)
# world info
world = World(robot)

# enable camera device
camera = robot.getDevice('camera')
camera.enable(time_step)

grid = Grid()

grid.add_artifact( Artifact("Orange", [0.12, -0.12, 1.79], (1, 1)) )
grid.add_artifact( Artifact("Apple", [0.37, 0.12, 1.79], (1, 3)) )
grid.add_artifact( Artifact("RubberDuck", [-0.12, 0.12, 1.79], (1, 1)) )
grid.add_artifact( Artifact("SoccerBall", [-0.37, -0.37, 1.81], (0, 3)) )
grid.add_artifact( Artifact("Wineglass", [-0.12, 0.37, 1.79], (0, 1)) )

grid.print_artifacts()

# spawn objects
root_node = robot.getRoot()
root_children = root_node.getField('children')

artifacts = grid.get_artifacts()

n = world.get_nodes_by_type('Robot')
for node in n:
    print(node.getTypeName())


for art in artifacts:
    name = art.get_name()
    coord = art.get_coord()

    root_children.importMFNodeFromString(-1, f'{name}{{ translation {coord[0]} {coord[1]} {coord[2]} }}')

    # configure soccerball radius
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

# create a FastAPI app
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

def generate_unique_id():
    return str(uuid.uuid4())

@app.get(base_route + 'robots')
async def send_robots() -> list[Robot_]:
    r_nodes = world.get_nodes_by_type('Robot')
    robots_list = []
    for r in r_nodes:
        name = r.getTypeName()
        position = [round(p, 1) for p in r.getPosition()] 
        id = generate_unique_id()
        robots_list.append(Robot_(id = id, name = name, position = position))
    return robots_list

@app.post(base_route)
async def receive_message(m_obj: Message_):
    m.set_message(m_obj.message)
    return {"message" : m_obj.message}

@app.post(base_route + 'control')
async def receive_control(c_obj: Message_):
    control.set_mode(c_obj.message)
    return {"message" : c_obj.message}

@app.get(base_route + 'tasks')
async def send_tasks() -> list[Task_]:
    if task_manager.is_empty(): 
        return []
    tasks = task_manager.get_tasks()
    t_ = []
    for t in tasks:
        tid = t.get_id()
        tname = t.get_name()
        top = 'PickPlace' if type(t.get_operation()) == PickPlace else ''
        ttarget = t.get_operation().get_target().get_name()
        t_.append(Task_(id = tid, name = tname, operation = top, target = ttarget))

    return t_

@app.post(base_route + 'tasks')
async def receive_task(t_obj: Task_):
    op = t_obj.operation

    match op:
        case 'PickPlace':
            art = grid.get_artifact(t_obj.target)
            operation = PickPlace(art)
            t = Task(t_obj.id, t_obj.name, operation) 
            task_manager.add_task(t)

    return t_obj

@app.delete(base_route + 'tasks/{task_id}')
def delete_task(task_id: str):
    task_manager.remove_task(task_id)
    return {"message": "Task deleted"}

# function to start the FastAPI server
def start_fastapi_server():
    uvicorn.run(app, host = API_URL, port = PORT)

# start the FastAPI server in a separate thread
fastapi_server_thread = threading.Thread(target=start_fastapi_server)
fastapi_server_thread.start()

# main loop:
if __name__ == '__main__':
    while True:
        control.monitor(robot, time_step)
        queue_len = receiver.getQueueLength()
        if queue_len > 0: 
            data = receiver.getBytes() 
            receiver.nextPacket()
            data = struct.unpack('d', data)
            d = int(data[0])
            if d == 1:
                task_pending = False

        if not task_manager.is_empty() and not task_pending:
            t = task_manager.get_task()
            task_pending = True
            t.execute(robot)

# Enter here exit cleanup code.
