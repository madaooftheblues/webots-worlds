class Task():
    def __init__(self, title, operation):
        self.title = title
        self.operation = operation

    def setTitle(self, title):
        self.title = title
        
    def getTitle(self):
        return self.title

class PickPlace(Task):
    def __init__(self, title, operation, target):
        super.__init__(title, operation)
        self.target = target

    def setTarget(self, target):
        self.target = target

    def getTarget(self):
        return self.target
        
        
    
