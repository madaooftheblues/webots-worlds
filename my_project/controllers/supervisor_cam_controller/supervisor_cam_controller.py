"""supervisor_cam_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Supervisor, Camera
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# create the Robot instance.
robot = Supervisor()

# Get the time step of the current world (simulation)
time_step = int(robot.getBasicTimeStep())

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
