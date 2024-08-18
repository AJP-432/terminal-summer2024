import json
from .sim_game_state import SimGameState

class Simulator:
    def __init__(self, last_action_frame: str, test: str) -> None:
        self.last_action_frame = json.loads(last_action_frame)
        self.test = json.loads(test)
        self.game_state = SimGameState(self.last_action_frame, self.test)
 
    def run_simulation(self) -> list[str]:
        while not self.game_state.is_round_over():
            self.game_state.run_frame()

        return self.game_state.get_results()