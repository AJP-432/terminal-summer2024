# from game import *
from .sim_game_state import SimGameState
from typing import List

# Format of test: 
        # {
        #   "p1Units": [WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, REMOVE, UPGRADE],
        #   "p2Units": [WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, REMOVE, UPGRADE]
        # }
class Simulator: 
    def __init__(self, config, game_state_string, tests):
        self.config = config
        self.serialized_string = game_state_string
        self.tests = tests

        self.game_state = None
        self.simulation_results = []
        self.run_simulations()

    def get_results(self):
        return self.simulation_results
    
    def run_simulations(self):
        for test in self.tests:
            self.game_state = SimGameState(self.config, self.serialized_string, test)
            res = self.simulation_loop()
            self.simulation_results.append(res)
            
    def simulation_loop(self, move) -> dict[str, List[float]]:
        """Having loaded game state, run simulation loop

        Returns:
            dict[str, List[float]]: game result summary
        """ 

        # Action Phase
        is_round_over = False
        while not is_round_over: 
            walkers = self.game_state.get_walkers()
            # If there are no walkers alive, the simulation is over
            if len(walkers) == 0:
                break

        # Give shields:
        for support in self.game_state.get_supports(): 
            # check if a new walker has entered and give it shield
            continue
    
        # Move walkers
        for walker in self.game_state.get_walkers():
            # Move walker
            continue

        # Attack
        self.damage_engine.attack(self.game_state)

        # Cleanup dead structures and supports
        self.game_state.cleanup()
            
        return self.game_state.get_summary()