from controller import Supervisor
from abc import ABC, abstractmethod
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
        # distance calculator
        def measure_dist(p1, p2):
            return math.dist(p1,p2)

        # choose which robot arm is to pick
        def choose_robot(self, coord: list):
            arm_1 = supervisor.getFromDef('ARM1')
            arm_2 = supervisor.getFromDef('ARM2')
            
            arm_1_coord = arm_1.getPosition()
            arm_2_coord = arm_2.getPosition()
            dist_1 = measure_dist(self.target.coord, arm_1_coord)
            dist_2 = measure_dist(self.target.coord, arm_2_coord)
            
            if dist_1 <= dist_2: return 1
            return 2


        # set emitter channe
        if not detect(self.target.name, supervisor): return
        selected_robot = choose_robot(self, self.target.coord)
        emitter = supervisor.getDevice('emitter')
        emitter.setChannel(selected_robot)
        coordinates = struct.pack("dd", self.target.pose[0], self.target.pose[1])
        emitter.send(coordinates)
        emitter.setChannel(3)
        tell_pioneer = struct.pack("d", int(selected_robot))
        emitter.send(tell_pioneer)
        emitter.setChannel(0)

class Task:
    def __init__(self, id, name, operation):
        self.id = id
        self.name = name
        self.operation = operation

    def set_title(self, title):
        self.title = title
        
    def get_title(self):
        return self.title

    def get_operation(self):
        return self.operation

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def execute(self, supervisor: Supervisor):
        self.operation.perform(supervisor)
        pass

class TaskManager:
    def __init__(self):
        self.queue = []
    
    def add_task(self, task: Task):
        self.queue.append(task)

    def get_tasks(self):
        return self.queue

    def get_task(self):
        if not self.is_empty():
            return self.queue.pop(0)

    def remove_task(self, task_id):
        self.queue[:] = [task for task in self.queue if task.id != task_id]

    def get_queue_len(self):
        return len(self.queue)

    def is_empty(self):
        return len(self.queue) == 0
