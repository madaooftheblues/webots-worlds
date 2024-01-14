from controller import Supervisor

class World:
    def __init__(self, supervisor: Supervisor):
        self.supervisor = supervisor

    def _get_children(self):
        root_node = self.supervisor.getRoot()
        root_children = root_node.getField('children')
        return root_children, root_children.getCount()

    def _get_nodes(self, filter_func):
        children, num_of_nodes = self._get_children()
        required_nodes = [
            node for i in range(num_of_nodes)
            if (node := children.getMFNode(i)) and filter_func(node)
        ]
        return required_nodes

    def get_node_by_name(self, node_name: str):
        required_nodes = self._get_nodes(lambda node: node.getTypeName() == node_name)
        return required_nodes[0] if len(required_nodes) > 0 else None

    def get_nodes_by_type(self, node_type: str):
        return self._get_nodes(lambda node: node.getBaseTypeName() == node_type)
 
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
    
    def get_artifact(self, name):
        arts = self.get_artifacts()
        for art in arts:
            if art.name == name:
                return art

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
