from controller import Supervisor

class Control:
    def __init__(self):
        self.mode = 'play'
    def set_mode(self, mode: str):
        self.mode = mode
    def get_mode(self):
        return self.mode

    def play(self, supervisor: Supervisor, timestep: float):
        supervisor.simulationSetMode(supervisor.SIMULATION_MODE_REAL_TIME)
        supervisor.step(timestep)

    def pause(self, supervisor: Supervisor):
        supervisor.simulationSetMode(supervisor.SIMULATION_MODE_PAUSE)
        supervisor.step(0)

    def reset(self, supervisor: Supervisor):
        supervisor.simulationReset()
        supervisor.restartController()

    def monitor(self, supervisor: Supervisor, timestep: float):
        if self.mode == 'play':
            self.play(supervisor, timestep)
        elif self.mode == 'pause':
            self.pause(supervisor)

