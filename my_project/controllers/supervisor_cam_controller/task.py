from controller import Supervisor
from abc import ABC, abstractmethod
from queue import Queue
from world import Artifact
import math
import struct
from object_detection import detect

class Operation:
    @abstractmethod
    def perform(self, supervisor: Supervisor):
        pass

class PickPlace(Operation):
    def __init__(self, target: Artifact):
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
        def choose_robot(self, coord: list):
            arm_1 = supervisor.getFromDef('ARM1')
            arm_2 = supervisor.getFromDef('ARM2')
            
            arm_1_coord = arm_1.getPosition()
            arm_2_coord = arm_2.getPosition()
            dist_1 = measure_dist(self.target.coord, arm_1_coord)
            dist_2 = measure_dist(self.target.coord, arm_2_coord)
            
            if dist_1 <= dist_2: return 1
            return 2


        # Set emitter channe
        if not detect(self.target.name, supervisor): return
        emitter = supervisor.getDevice('emitter')
        emitter.setChannel(choose_robot(self, self.target.coord))
        coordinates = struct.pack("dd", self.target.pose[0], self.target.pose[1])
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
