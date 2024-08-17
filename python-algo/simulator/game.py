
import json

class Game:
    def __init__(self, round_starting_frame_string):
        self.frame = round_starting_frame_string
        self.frame_number = 0
        self.is_round_over = False
        self.newest_id = 0
        # self.pathfinding = Pathfinding()
        # self.targeting = Targeting()
        self.units = {}
        self.structures = {}
        self.map = [[[j, i] for i in range(5)] for j in range(5)]

        # setup units and structures in position w respective health and stats
    def get_unique_id(self):
        self.newest_id += 1
        return self.newest_id

    def parse_round_starting_frame_string(self):
        self.frame = json.loads(self.round_starting_frame_string)
        return self.round_starting_frame_string.split()

    def run_frame(self):
        pass
        # for all supports, heal
        # for all units, move them
        # for all structures, attack
        
    def end_round(self):
        return self.is_round_over
    
    def get_game_state(self):
        return json.dumps(self.frame)