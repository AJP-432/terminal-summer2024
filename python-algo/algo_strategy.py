import gamelib
import random
import math
import warnings
from sys import maxsize
import json
from enum import Enum


class MapEdges(Enum):
    TOP_RIGHT = 0
    TOP_LEFT = 1
    BOTTOM_LEFT = 2
    BOTTOM_RIGHT = 3


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips:

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical
  board states. Though, we recommended making a copy of the map to preserve
  the actual current map state.
"""


class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """
        Read in config and perform any initial setup here
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP, is_attacking, just_attacked, UNIT_TYPE_TO_INDEX
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        UNIT_TYPE_TO_INDEX = {
            WALL: 0,
            SUPPORT: 1,
            TURRET: 2,
            SCOUT: 3, 
            DEMOLISHER: 4,
            INTERCEPTOR: 5,
        }
        MP = 1
        SP = 0
        is_attacking = False
        just_attacked = False

        self.first_action_frame = None
        self.last_action_frame = None
        # This is a good place to do initial setup
        self.scored_on_locations = []

        self.scout_count = [0]

        # Enemy MP and Attack Turns
        self.enemy_mp = []
        self.enemy_hp = [30]
        self.enemy_scout_count = [0]

        # attack location results
        self.should_attack_mid = None
        self.mid_attack_health = 0
        self.should_attack_back = None
        self.back_attack_health = 0
        # round 2 this set to True
        self.should_attack_edge = None
        self.edge_attack_health = 0
        self.min_resource_needed = 11

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(
            game_state.turn_number))
        # Comment or remove this line to enable warnings.

        if game_state.turn_number > 0:
            self.collect_data()
        game_state.suppress_warnings(True)

        self.starter_strategy(game_state)

        game_state.submit_turn()

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def starter_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some interceptors early on.
        We will place turrets near locations the opponent managed to score on.
        For offense we will use long range demolishers if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Scouts to try and score quickly.
        """

        if game_state.turn_number == 2:
            self.should_attack_edge = True
            can_attack_edge = self.find_edge_holes_enemy(game_state)
            if can_attack_edge == 'left':
                self.spawn_reactive_support(game_state, [1, 12])
                game_state.attempt_spawn(SCOUT, [1, 12], 1000)
                self.remove_supports(game_state, [1, 12])
            elif can_attack_edge == 'right':
                self.spawn_reactive_support(game_state, [26, 12])
                game_state.attempt_spawn(SCOUT, [26, 12], 1000)
                self.remove_supports(game_state, [26, 12])
            else:
                game_state.attempt_spawn(SCOUT, [13, 0], 1000)
        
        if game_state.turn_number > 2: 
            last_scout_count = self.scout_count[-1]
            if last_scout_count > 0: 
                # Check if did damage
                if self.enemy_hp[-2] - self.enemy_hp[-1] > 0:
                    ...
                else:
                    self.min_resource_needed += 3
                    # reset if it fails 
                    if self.min_resource_needed > 17:
                        self.min_resource_needed = 11
                

        if game_state.turn_number > 2  and game_state.turn_number <= 8 and game_state.get_resource(1) >= self.min_resource_needed:
            best_location = self.all_attacks(game_state)
            if best_location is not None:
                self.spawn_reactive_support(game_state, best_location[0])
                game_state.attempt_spawn(SCOUT, best_location[0], 1000)
                self.remove_supports(game_state, best_location[0])
            else:
                min_damage = min(self.mid_attack_health, self.back_attack_health, self.edge_attack_health)
                gamelib.debug_write("Min damage: {}".format(min_damage))
                if min_damage == self.mid_attack_health:
                    if self.should_attack_mid == 'left':
                        self.spawn_reactive_support(game_state, [22, 8])
                        game_state.attempt_spawn(SCOUT, [22, 8], 1000)
                        self.remove_supports(game_state, [22, 8])
                    elif self.should_attack_mid == 'right':
                        self.spawn_reactive_support(game_state, [5, 8])
                        game_state.attempt_spawn(SCOUT, [5, 8], 1000)
                        self.remove_supports(game_state, [5, 8])
                elif min_damage == self.back_attack_health:
                    if self.should_attack_back == 'left':
                        self.spawn_reactive_support(game_state, [14, 0])
                        game_state.attempt_spawn(SCOUT, [14, 0], 1000)
                        self.remove_supports(game_state, [14, 0])
                    elif self.should_attack_back == 'right':
                        self.spawn_reactive_support(game_state, [13, 0])
                        game_state.attempt_spawn(SCOUT, [13, 0], 1000)
                        self.remove_supports(game_state, [13, 0])
                elif min_damage == self.edge_attack_health:
                    if self.should_attack_edge == 'left':
                        self.spawn_reactive_support(game_state, [1, 12])
                        game_state.attempt_spawn(SCOUT, [1, 12], 1000)
                        self.remove_supports(game_state, [1, 12])
                    elif self.should_attack_edge == 'right':
                        self.spawn_reactive_support(game_state, [26, 12])
                        game_state.attempt_spawn(SCOUT, [26, 12], 1000)
                        self.remove_supports(game_state, [26, 12])

        if game_state.turn_number > 8 and game_state.get_resource(1) >= 13:
            best_location = self.all_attacks(game_state)
            if best_location is not None:
                self.spawn_reactive_support(game_state, best_location[0])
                game_state.attempt_spawn(SCOUT, best_location[0], 1000)
                self.remove_supports(game_state, best_location[0])
            else:
                min_damage = min(self.mid_attack_health, self.back_attack_health, self.edge_attack_health)
                gamelib.debug_write("Min damage: {}".format(min_damage))
                if min_damage == self.mid_attack_health:
                    if self.should_attack_mid == 'left':
                        self.spawn_reactive_support(game_state, [22, 8])
                        game_state.attempt_spawn(SCOUT, [22, 8], 1000)
                        self.remove_supports(game_state, [22, 8])
                    elif self.should_attack_mid == 'right':
                        self.spawn_reactive_support(game_state, [5, 8])
                        game_state.attempt_spawn(SCOUT, [5, 8], 1000)
                        self.remove_supports(game_state, [5, 8])
                elif min_damage == self.back_attack_health:
                    if self.should_attack_back == 'left':
                        self.spawn_reactive_support(game_state, [14, 0])
                        game_state.attempt_spawn(SCOUT, [14, 0], 1000)
                        self.remove_supports(game_state, [14, 0])
                    elif self.should_attack_back == 'right':
                        self.spawn_reactive_support(game_state, [13, 0])
                        game_state.attempt_spawn(SCOUT, [13, 0], 1000)
                        self.remove_supports(game_state, [13, 0])
                elif min_damage == self.edge_attack_health:
                    if self.should_attack_edge == 'left':
                        self.spawn_reactive_support(game_state, [1, 12])
                        game_state.attempt_spawn(SCOUT, [1, 12], 1000)
                        self.remove_supports(game_state, [1, 12])
                    elif self.should_attack_edge == 'right':
                        self.spawn_reactive_support(game_state, [26, 12])
                        game_state.attempt_spawn(SCOUT, [26, 12], 1000)
                        self.remove_supports(game_state, [26, 12])

                # if self.should_attack_mid == 'left':
                #     self.spawn_reactive_support(game_state, best_mid_left[0])
                #     game_state.attempt_spawn(SCOUT, best_mid_left[0], 1000)
                #     self.remove_supports(game_state, best_mid_left[0])
                # elif self.should_attack_mid == 'right':
                #     best_mid_right = self.least_damage_spawn_location(game_state, [[4, 9], [5, 8], [6, 7], [7, 6], [8, 5]])
                #     self.spawn_reactive_support(game_state, best_mid_right[0])
                #     game_state.attempt_spawn(SCOUT, best_mid_right[0], 1000)
                #     self.remove_supports(game_state, best_mid_right[0])
                # if self.should_attack_back == 'left':
                #     best_back_left = self.least_damage_spawn_location(game_state, [[14, 0]])
                #     self.spawn_reactive_support(game_state, best_back_left[0])
                #     game_state.attempt_spawn(SCOUT, best_back_left[0], 1000)
                #     self.remove_supports(game_state, best_back_left[0])
                # elif self.should_attack_back == 'right':
                #     best_back_right = self.least_damage_spawn_location(game_state, [[13, 0]])
                #     self.spawn_reactive_support(game_state, best_back_right[0])
                #     game_state.attempt_spawn(SCOUT, best_back_right[0], 1000)
                #     self.remove_supports(game_state, best_back_right[0])
                # if self.should_attack_edge == 'left':
                #     best_edge_left = self.least_damage_spawn_location(game_state, [[1, 12], [1, 12]])
                #     self.spawn_reactive_support(game_state, best_edge_left[0])
                #     game_state.attempt_spawn(SCOUT, best_edge_left[0], 1000)
                #     self.remove_supports(game_state, best_edge_left[0])
                # elif self.should_attack_edge == 'right':
                #     best_edge_right = self.least_damage_spawn_location(game_state, [[26, 12], [26, 12]])
                #     self.spawn_reactive_support(game_state, best_edge_right[0])
                #     game_state.attempt_spawn(SCOUT, best_edge_right[0], 1000)
                #     self.remove_supports(game_state, best_edge_right[0])
            
            self.should_attack_mid = None
            self.back_attack_health = float('inf')
            self.should_attack_back = None
            self.edge_attack_health = float('inf')
            self.should_attack_edge = None
            self.edge_attack_health = float('inf')
                
        
        self.build_defences(game_state)


    def all_attacks(self, game_state):
        # use least damage location
        self.should_attack_mid, self.mid_attack_health = self.check_middle_attack(game_state, game_state.get_resource(1))
        self.should_attack_back, self.back_attack_health = self.check_back_attack(game_state)
        self.should_attack_edge, self.edge_attack_health = self.check_edge_attack(game_state)
        best_location = None

        if self.should_attack_mid is not None and self.should_attack_back is not None and self.should_attack_edge is not None:
            best_list = []
            if self.should_attack_mid == 'left':
                best_list.append([[22, 8], self.mid_attack_health])
            elif self.should_attack_mid == 'right':
                best_list.append([[5, 8], self.mid_attack_health])
            if self.should_attack_back == 'left':
                best_list.append([[14, 0], self.back_attack_health])
            elif self.should_attack_back == 'right':
                best_list.append([[13, 0], self.back_attack_health])
            if self.should_attack_edge == 'left':
                best_list.append([[1, 12], self.edge_attack_health])
            elif self.should_attack_edge == 'right':
                best_list.append([[26, 12], self.edge_attack_health])
                
            damage_dict = {
            'mid': self.mid_attack_health if self.should_attack_mid is not None else float('inf'),
            'back': self.back_attack_health if self.should_attack_back is not None else float('inf'),
            'edge': self.edge_attack_health if self.should_attack_edge is not None else float('inf'),
            }
            gamelib.debug_write("Damage dict: {}".format(damage_dict))
        # Find the key with the minimum value
            min_damage_location = min(damage_dict, key=damage_dict.get)
            min_damage = damage_dict[min_damage_location]

        # Find the corresponding location tuple
            best_location = next(loc for loc in best_list if loc[1] == min_damage)

        return best_location
    
    def initial_build(self, game_state):
        """
        Creates initial defence build with a hole center-right (C) and rest have upgraded turrets and wall
        """
        turrets = [[4, 12], [10, 12], [17, 12], [23, 12]]
        walls = [[4, 13], [10, 13], [17, 13], [23, 13]]
        game_state.attempt_spawn(TURRET, turrets)
        # game_state.attempt_upgrade(turrets[0])
        # game_state.attempt_upgrade(turrets[1])
        # game_state.attempt_upgrade(turrets[3])
        game_state.attempt_upgrade(turrets)
        game_state.attempt_spawn(WALL, walls)
        game_state.attempt_upgrade(walls)
    
        # If we were attacked in the last turn, we know that this turn they cant attack again
        # and that we should rebuild core defense (instead of spending it elsewhere)
        # this only detects for weak guys, as the initial build will rebuild naturally
        if self.enemy_scout_count[-1] > 3:
            for loc in (turrets + walls):
                unit = game_state.contains_stationary_unit(loc)
                if unit and unit.health < 0.25 * unit.max_health:
                    game_state.attempt_remove(loc)
            
    def get_path(self, game_state, location):
        target_edge = game_state.get_target_edge(location)
        edges = game_state.game_map.get_edge_locations(target_edge)
        path = game_state._shortest_path_finder.navigate_multiple_endpoints(location, edges, game_state)
        return path

    def build_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy demolishers can attack them.
        """
        # Useful tool foandr setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download


        second_turrets = [[3, 12], [24, 12]]
        third_turrets = [[11, 12], [16, 12]]
        fourth_turrets = [[2, 13], [25, 13]]
        
        second_walls = [[3, 13], [24, 13]]
        third_walls = [[11, 13], [16, 13]]
        fourth_walls = [[0, 13], [27, 13]]

        self.initial_build(game_state)

        # round 2 bait
        # if game_state.turn_number == 2:


        for i in range(len(second_turrets)):
            game_state.attempt_spawn(TURRET, second_turrets[i])
            game_state.attempt_spawn(WALL, second_walls[i])
            game_state.attempt_upgrade(second_turrets[i])
            game_state.attempt_upgrade(second_walls[i])

        for i in range(len(third_turrets)):
            game_state.attempt_spawn(TURRET, third_turrets[i])
            game_state.attempt_spawn(WALL, third_walls[i])
            game_state.attempt_upgrade(third_turrets[i])
            game_state.attempt_upgrade(third_walls[i])
        game_state.attempt_spawn(WALL, fourth_walls)

        # make sure everything else built before go to fourth wave
        test_unit1 = game_state.contains_stationary_unit([16, 13])
        test_unit2 = game_state.contains_stationary_unit([16, 12])
        if test_unit1 and test_unit2 and test_unit1.upgraded and test_unit2.upgraded:
            for i in range(len(fourth_turrets)):
                game_state.attempt_spawn(TURRET, fourth_turrets[i])
                game_state.attempt_upgrade(fourth_turrets[i])
        
    def check_middle_attack(self, game_state, scouts):
        # returns opp side to attack (i.e. if returned left, attack towards left middle)
        # if None, do not attack middle
        
        middle_locs = [[9, 18], [10, 18], [11, 18], [12, 18], [13, 18], [14, 18], [15, 18], [16, 18], [17, 18], [18, 18], [8, 17], [9, 17], [10, 17], [11, 17], [12, 17], [13, 17], [14, 17], [15, 17], [16, 17], [17, 17], [18, 17], [19, 17], [7, 16], [8, 16], [9, 16], [10, 16], [11, 16], [12, 16], [13, 16], [14, 16], [15, 16], [
            16, 16], [17, 16], [18, 16], [19, 16], [20, 16], [7, 15], [8, 15], [9, 15], [10, 15], [11, 15], [12, 15], [13, 15], [14, 15], [15, 15], [16, 15], [17, 15], [18, 15], [19, 15], [20, 15], [7, 14], [8, 14], [9, 14], [10, 14], [11, 14], [12, 14], [13, 14], [14, 14], [15, 14], [16, 14], [17, 14], [18, 14], [19, 14], [20, 14]]

        left_turrets = 0
        right_turrets = 0
        for loc in middle_locs:
            unit = game_state.contains_stationary_unit(loc)
            if unit and loc[0] < 14 and unit.unit_type == TURRET:
                if unit.upgraded:
                    left_turrets += 3 * (unit.health / unit.max_health)
                else:
                    left_turrets += 1 * (unit.health / unit.max_health)
            elif unit and loc[0] >= 14 and unit.unit_type == TURRET:
                if unit.upgraded:
                    right_turrets += 3 * (unit.health / unit.max_health)
                else:
                    right_turrets += 1 * (unit.health / unit.max_health)
        
        if left_turrets <= 225 and scouts >= 11:
            # attack left
            return 'left', left_turrets
        elif right_turrets <= 225 and scouts >= 11:
            # attack right
            return 'right', right_turrets
        elif left_turrets <= 300 and scouts >= 11:
            return 'left', left_turrets
        elif right_turrets <= 300 and scouts >= 11:
            return 'right', right_turrets
        elif left_turrets <= 450 and right_turrets <= 300 and scouts >= 14:
            return 'left', left_turrets
        elif right_turrets <= 450 and left_turrets <= 300 and scouts >= 14:
            return 'right', right_turrets
        elif left_turrets <= 450 and right_turrets <= 450 and scouts >= 16:
            return 'left', left_turrets
        elif left_turrets <= 450 and right_turrets <= 450 and scouts >= 16:
            return 'right', right_turrets
        else:
            return None, float('inf')

    def find_edge_holes_enemy(self, game_state):
        left_edge_locations = [[0, 14], [1, 14], [2, 14]]
        left_second_edges = [[1, 15], [2, 15]]
        right_edge_locations = [[25, 14], [26, 14], [27, 14]]
        right_second_edges = [[25, 15], [26, 15]]
        
        for location in left_edge_locations:
            if not game_state.contains_stationary_unit(location):
                count = 0
                for loc in left_second_edges:
                    if not game_state.contains_stationary_unit(loc):
                        count += 1
                if count == 2:
                    return 'left'
                
        for location in right_edge_locations:
            if not game_state.contains_stationary_unit(location):
                count = 0
                for loc in right_second_edges:
                    if not game_state.contains_stationary_unit(loc):
                        count += 1
                if count == 2:
                    return 'right'
        return None
    
    def check_edge_attack(self, game_state):
        """
        Returns location to spawn from [x,y] or None
        """
        edge_spawns = [[1, 12], [26, 12]]

        edge_hole = self.find_edge_holes_enemy(game_state)
        if edge_hole is None:
            return None, float('inf')

        best_location = None
        weakest_side_health = float("inf")
        for location in edge_spawns:
            path = self.get_path(game_state, location)

            total_oppo_health_scaled = 0
            
            if not path:
                continue
            for path_location in path:
                # only check the first bit of the path for top edge spawn
                if location[1] > 19:
                    continue
                    
                visible_locations = game_state.game_map.get_locations_in_range(path_location, self.config["unitInformation"][3]["attackRange"]) # 3 = scouts
                # check how much health the opponent has in our FOV
                for loc in visible_locations:
                    unit = game_state.contains_stationary_unit(loc)
                    # don't consider if there is no unit, it's our unit or it's not a turret
                    if not unit or unit.player_index == 0 or unit.unit_type != TURRET:
                        continue
                    oppo_health = (unit.health / unit.max_health) * (3 if unit.upgraded else 1)
                    total_oppo_health_scaled += oppo_health
            
                if total_oppo_health_scaled < weakest_side_health:
                    weakest_side_health = total_oppo_health_scaled
                    best_location = 'left' if location == edge_spawns[0] else 'right'

        return best_location, weakest_side_health

    def check_back_attack(self, game_state):
        back_spawns = [[13, 0], [14, 0]]

        edge_hole = self.find_edge_holes_enemy(game_state)
        if edge_hole is None:
            return None, float('inf')

        best_location = None
        weakest_side_health = float("inf")

        for location in back_spawns:
            path = self.get_path(game_state, location)

            total_oppo_health_scaled = 0
            if not path:
                continue
            for path_location in path:
                # only check the first bit of the path for top edge spawn
                if location[1] < 10:
                    continue
                    
                visible_locations = game_state.game_map.get_locations_in_range(path_location, self.config["unitInformation"][3]["attackRange"]) # 3 = scouts
                # check how much health the opponent has in our FOV
                for loc in visible_locations:
                    unit = game_state.contains_stationary_unit(loc)
                    # don't consider if there is no unit, it's our unit or it's not a turret
                    if not unit or unit.player_index == 0 or unit.unit_type != TURRET:
                        continue
                    oppo_health = (unit.health / unit.max_health) * (3 if unit.upgraded else 1)
                    total_oppo_health_scaled += oppo_health
            
                if total_oppo_health_scaled < weakest_side_health:
                    weakest_side_health = total_oppo_health_scaled
                    best_location = 'right' if location == [13, 0] else 'left'
                i += 1

        return best_location, weakest_side_health



    def check_back_attack2(self, game_state):
        left_close = [[2, 16], [3, 16], [4, 16], [1, 15], [2, 15], [3, 15], [0, 14], [1, 14], [2, 14]]
        left_far = [[5, 16], [4, 15], [5, 15], [3, 14], [4, 14], [5, 14]]

        right_close = [[23, 16], [24, 16], [25, 16], [24, 15], [25, 15], [26, 15], [25, 14], [26, 14], [27, 14]]
        right_far = [[22, 16], [22, 15], [23, 15], [22, 14], [23, 14], [24, 14]]

        left, right = 0, 0
        # LEFT
        for loc in left_close:
            unit = game_state.contains_stationary_unit(loc)
            if unit and unit.unit_type == TURRET: 
                left += (3 if unit.upgraded else 1) * (unit.health / unit.max_health)

        for loc in left_far:
            unit = game_state.contains_stationary_unit(loc)
            if unit and unit.unit_type == TURRET:
                left += (3 if unit.upgraded else 0) * (unit.health / unit.max_health)
        
        # RIGHT
        for loc in right_close:
            unit = game_state.contains_stationary_unit(loc)
            if unit and unit.unit_type == TURRET: 
                right += (3 if unit.upgraded else 1) * (unit.health / unit.max_health)

        for loc in right_far:
            unit = game_state.contains_stationary_unit(loc)
            if unit and unit.unit_type == TURRET:
                right += (3 if unit.upgraded else 0) * (unit.health / unit.max_health)
        
        if left > right:
            return 'right'
        else:
            return 'left'

    def spawn_reactive_support(self, game_state, attack_location):
        if attack_location[0] < 12:
            game_state.attempt_spawn(
                SUPPORT, [attack_location[0] + 1, attack_location[1] - 1])
        elif attack_location[0] >= 12 and attack_location[0] <= 13:
            game_state.attempt_spawn(SUPPORT, [13, 2])
        elif attack_location[0] > 15:
            game_state.attempt_spawn(
                SUPPORT, [attack_location[0] - 1, attack_location[1] - 1])
        elif attack_location[0] >= 14 and attack_location[0] <= 15:
            game_state.attempt_spawn(SUPPORT, [14, 2])

    def remove_supports(self, game_state, support_location=None):
        supports = [[13, 2], [14, 2], [13, 3], [14, 3]]
        for support in supports:
            if game_state.contains_stationary_unit(support):
                game_state.attempt_remove(support)
        if support_location:
            if support_location[0] < 12:
                game_state.attempt_remove(
                    [support_location[0] + 1, support_location[1] - 1])
            elif support_location[0] >= 12 and support_location[0] <= 13:
                game_state.attempt_remove([13, 2])
            elif support_location[0] > 15:
                game_state.attempt_remove(
                    [support_location[0] - 1, support_location[1] - 1])
            elif support_location[0] >= 14 and support_location[0] <= 15:
                game_state.attempt_remove([14, 2])

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = self.get_path(game_state, location)
            damage = 0
            if path:
                for path_location in path:
                    # Get number of enemy turrets that can attack each location and multiply by turret damage
                    damage += len(game_state.get_attackers(path_location, 0)) * \
                        gamelib.GameUnit(TURRET, game_state.config).damage_i
                damages.append(damage)
        return location_options[damages.index(min(damages))], min(damages)

    def opponent_weakest_health_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        pass
        # for location in location_options:
        #     target_edge = game_state.get_target_edge(location)
        #     edges = game_state.game_map.get_edge_locations(target_edge)
        #     path = game_state._shortest_path_finder.navigate_multiple_endpoints(
        #         location, edges, game_state)

        #     #  for unit in

    def deals_most_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        pass

        # damages = []
        # # Get the damage estimate each path will take
        # for location in location_options:
        #     target_edge = game_state.get_target_edge(location)
        #     edges = game_state.game_map.get_edge_locations(target_edge)
        #     path = game_state._shortest_path_finder.navigate_multiple_endpoints(location, edges, game_state)
        #     damage = 0
        #     for path_location in path:
        #         target_= game_state.get_target(game_state.game_map[location])

        # Now just return the location that takes the least damage
        # return location_options[damages.index(min(damages))], min(damages)

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called 
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at in json-docs.html in the root of the Starterkit.
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        if state["turnInfo"][2] == 0:
            self.first_action_frame = state
        self.last_action_frame = state
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly,
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write(
                    "All locations: {}".format(self.scored_on_locations))

    def collect_data(self):
        # Collect enemy MP and attack spawn
        scouts = len(self.first_action_frame["p1Units"][3])
        self.scout_count.append(scouts)

        health = self.last_action_frame["p2Stats"][0]
        mp = self.last_action_frame["p2Stats"][2]
        enemy_scouts = len(self.first_action_frame["p2Units"][3])

        self.enemy_mp.append(mp)
        self.enemy_hp.append(health)
        self.enemy_scout_count.append(enemy_scouts)


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
