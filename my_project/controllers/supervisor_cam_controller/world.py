from controller import Supervisor
 
class Artifact:
    def __init__(self, name, coord, pose):
        self.name = name
        self.coord = coord
        self.pose = pose

    def get_name(self):
        return self.name

    def get_pose(self):
        return self.pose

    def get_coord(self):
        return self.coord

    def set_name(self, name: str):
        self.name = name

    def set_pose(self, pose):
        self.pose = pose

    def set_coord(self, coord: list):
        self.coord = coord

class Grid:
    def __init__(self):
        self.artifacts = []

    def get_artifacts(self):
        return self.artifacts

    def add_artifact(self, artifact: Artifact):
        self.artifacts.append(artifact)

    def remove_artifact(self, name):
        for i, art in enumarate(self.artifacts):
            if art.name == name:
                self.artifacts.pop(i)

    def clear_artifacts(self):
        self.artifacts.clear()

    def print_artifacts(self):
        for art in self.artifacts:
            print(art.name, art.coord, art.pose)
