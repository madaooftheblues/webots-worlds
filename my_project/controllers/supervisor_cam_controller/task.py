from controller import Supervisor
from abc import ABC, abstractmethod
from queue import Queue

class Operation:
    @abstractmethod
    def perform(self, supervisor: Supervisor):
        pass

class PickPlace(Operation):
    def __init__(self, target: str):
        self.target = target

    def set_target(self, target):
        self.target = target

    def get_target(self):
        return self.target

    def perform(self, supervisor: Supervisor):
        # Distance calculator
        def measure_dist(p1, p2):
            return math.dist(p1,p2)

        # Choose which robot arm is to pick
        def choose_robot():
            arm_1 = supervisor.getFromDef('ARM1')
            arm_2 = supervisor.getFromDef('ARM2')
            
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

class Task:
    def __init__(self, title, operation):
        self.title = title
        self.operation = operation

    def set_title(self, title):
        self.title = title
        
    def get_title(self):
        return self.title

    def execute(self, supervisor: Supervisor):
        self.operation.perform(supervisor)
        pass

class TaskManager:
    def __init__(self):
        self.queue = Queue(maxsize = 20)
    
    def add_task(self, task: Task):
        self.queue.put_nowait(task)
    
    def get_task(self):
        return self.queue.get_nowait()
