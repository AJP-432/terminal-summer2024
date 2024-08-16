import gamelib
import random
import math
import warnings
from sys import maxsize
import json


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
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0
        # This is a good place to do initial setup
        self.scored_on_locations = []
        self.turn = 0
        self.current_opp_health = 0

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

        self.build_defences(game_state)

        if game_state.turn_number < 1:
            game_state.attempt_spawn(SCOUT, [7, 6], 5)
       
        # if defense_side == 'left':
        #     game_state.attempt_spawn(SCOUT, [0, 13], 1000)
        # elif defense_side == 'right':
        #     game_state.attempt_spawn(DEMOLISHER, [16, 2], 3)
        #     game_state.attempt_spawn(SCOUT, [27, 13], 1000)
        # else:
        #     game_state.attempt_spawn(SCOUT, [0, 13], 1000)
        #     game_state.attempt_spawn(SCOUT, [27, 13], 1000) 

        defense_side, most_supports_side = self.check_defense_side(game_state)

        if game_state.get_resource(1) >= 11 and game_state.turn_number < 6 and defense_side == 'left':
           # game_state.attempt_spawn(DEMOLISHER, [12, 1], 3)
           # game_state.attempt_spawn(SCOUT, [12, 1], int((game_state.get_resource(1) / 2) - 1))
            game_state.attempt_spawn(SCOUT, [13, 0], 1000)
        elif game_state.get_resource(1) >= 11 and game_state.turn_number < 6 and defense_side == 'right':
           # game_state.attempt_spawn(SCOUT, [15, 1], int((game_state.get_resource(1) / 2) - 1))
            game_state.attempt_spawn(SCOUT, [14, 0], 1000)

        if game_state.get_resource(1) > 16 and game_state.turn_number >= 6 and defense_side == 'left':
           # game_state.attempt_spawn(SCOUT, [12, 1], int((game_state.get_resource(1) / 2) - 1))
            game_state.attempt_spawn(SCOUT, [13, 0], 1000)
        elif game_state.get_resource(1) > 16 and game_state.turn_number >= 6 and defense_side == 'right':
           # game_state.attempt_spawn(SCOUT, [15, 1], int((game_state.get_resource(1) / 2) - 1))
            game_state.attempt_spawn(SCOUT, [14, 0], 1000)



    def build_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy demolishers can attack them.
        """
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download

        # NOTE: change some of these walls to turrets!!
        first_walls = [[0, 13], [1, 13], [27, 13], [26, 13]]
        second_walls = [[2, 13], [3, 13], [24, 13], [25, 13]]
        first_turrets = [[4, 12], [10, 12], [18, 12], [23, 12]]
        second_turrets = [[7, 13], [21, 13], [1, 12], [26, 12], [14, 13]]
        supports = [[13, 2], [14, 2]]
        extra_walls = [[4, 13], [9, 13], [10, 13], [18, 13], [19, 13], [23, 13], [2, 12], [25, 12]]
        extra_supports = [[13, 3], [14, 3], [13, 4], [14, 4], [14, 5], [13, 5]]
        
        # if health is = 30, keep building, attack after fifth turrets are built, every 4-5 rounds
        # else start attacking every 4-5 turns after spawning what can
        # if enemy damage going down, keep attacking same place
        # if not doing damage, switch to other side to open walls
        # use 2 waves of supported scouts


        if game_state.turn_number >= 2:
            most_attacked_side = self.check_attack_side()
            if most_attacked_side == 'left':
            # prioritize building on left
                game_state.attempt_spawn(TURRET, first_turrets[0])
                game_state.attempt_upgrade(first_turrets[0])
                game_state.attempt_spawn(TURRET, second_turrets[2])
                game_state.attempt_upgrade(second_turrets[2])
                game_state.attempt_spawn(WALL, first_walls[0])
                game_state.attempt_spawn(WALL, first_walls[1])
                game_state.attempt_spawn(WALL, second_walls[0])
                game_state.attempt_spawn(WALL, second_walls[1])
                game_state.attempt_spawn(TURRET, second_turrets[0])
                game_state.attempt_upgrade(first_walls[0])
                game_state.attempt_upgrade(first_walls[1])
                game_state.attempt_upgrade(second_walls[0])
                game_state.attempt_upgrade(second_walls[3])
                game_state.attempt_upgrade(second_turrets[1])
                game_state.attempt_spawn(TURRET, [3, 11])
                game_state.attempt_upgrade([3, 11])
                game_state.attempt_upgrade([7, 13])
            elif most_attacked_side == 'right':
            # prioritize building on right
                game_state.attempt_spawn(TURRET, first_turrets[3])
                game_state.attempt_upgrade(first_turrets[3])
                game_state.attempt_spawn(TURRET, second_turrets[3])
                game_state.attempt_upgrade(second_turrets[3])
                game_state.attempt_spawn(WALL, first_walls[2])
                game_state.attempt_spawn(WALL, first_walls[3])
                game_state.attempt_spawn(WALL, second_walls[2])
                game_state.attempt_spawn(WALL, second_walls[3])
                game_state.attempt_spawn(TURRET, second_turrets[1])
                game_state.attempt_upgrade(first_walls[2])
                game_state.attempt_upgrade(first_walls[3])
                game_state.attempt_upgrade(second_walls[2])
                game_state.attempt_upgrade(second_walls[3])
                game_state.attempt_upgrade(second_turrets[1])
                game_state.attempt_spawn(TURRET, [24, 11])
                game_state.attempt_upgrade([24, 11])
                game_state.attempt_upgrade([21, 13])
                
        # runs if attacked locations are equal or all other defenses built
        game_state.attempt_spawn(WALL, first_walls)
        game_state.attempt_spawn(TURRET, first_turrets)
        game_state.attempt_upgrade(first_turrets)

        game_state.attempt_spawn(SUPPORT, supports[0])

        game_state.attempt_upgrade(first_walls)
        game_state.attempt_spawn(WALL, second_walls)
        game_state.attempt_spawn(SUPPORT, supports[1])
        game_state.attempt_upgrade(second_walls)

        game_state.attempt_spawn(SUPPORT, extra_supports[1])
        game_state.attempt_spawn(TURRET, second_turrets)
        game_state.attempt_upgrade(second_turrets)
        game_state.attempt_spawn(SUPPORT, extra_supports[0])

        game_state.attempt_upgrade(second_turrets)
        game_state.attempt_spawn(WALL, extra_walls)
        game_state.attempt_spawn(SUPPORT, extra_supports)
        game_state.attempt_upgrade(extra_walls)
        
        game_state.attempt_upgrade(supports)
        game_state.attempt_upgrade(extra_supports)
        game_state.attempt_spawn(SUPPORT, extra_supports)
        game_state.attempt_upgrade(extra_supports)





        # if turret health gets low, try to replace!!
        # use unit.health to get current health and unit.max_health to see when health is below half
        # for location in first_turrets:
        #     if game_state.contains_stationary_unit(location):
        #         unit = game_state.contains_stationary_unit(location)
        #         if unit.health < unit.max_health / 2.0:
        #             game_state.attempt_remove(location)
        # for location in second_turrets:
        #     if game_state.contains_stationary_unit(location):
        #         unit = game_state.contains_stationary_unit(location)
        #         if unit.health < unit.max_health / 2.0:
        #             game_state.attempt_remove(location)
        # for location in third_turrets:
        #     if game_state.contains_stationary_unit(location):
        #         unit = game_state.contains_stationary_unit(location)
        #         if unit.health < unit.max_health / 2.0:
        #             game_state.attempt_remove(location)
        # for location in fourth_turrets:
        #     if game_state.contains_stationary_unit(location):
        #         unit = game_state.contains_stationary_unit(location)
        #         if unit.health < unit.max_health / 2.0:
        #             game_state.attempt_remove(location)
        
        # do same for walls
        # for location in walls:
        #     if game_state.contains_stationary_unit(location):
        #         unit = game_state.contains_stationary_unit(location)
        #         if unit.health < unit.max_health / 2.0:
        #             game_state.attempt_remove(location)



    def check_defense_side(self, game_state):
        left_locations = [[13, 27], [12, 26], [13, 26], [11, 25], [12, 25], [13, 25], [10, 24], [11, 24], [12, 24], [13, 24], [9, 23], [10, 23], [11, 23], [12, 23], 
                          [13, 23], [8, 22], [9, 22], [10, 22], [11, 22], [12, 22], [13, 22], [7, 21], [8, 21], [9, 21], [10, 21], [11, 21], [12, 21], [13, 21], [6, 20], 
                          [7, 20], [8, 20], [9, 20], [10, 20], [11, 20], [12, 20], [13, 20], [5, 19], [6, 19], [7, 19], [8, 19], [9, 19], [10, 19], [11, 19], [12, 19], 
                          [13, 19], [4, 18], [5, 18], [6, 18], [7, 18], [8, 18], [9, 18], [10, 18], [11, 18], [12, 18], [13, 18], [3, 17], [4, 17], [5, 17], [6, 17], 
                          [7, 17], [8, 17], [9, 17], [10, 17], [11, 17], [12, 17], [13, 17], [2, 16], [3, 16], [4, 16], [5, 16], [6, 16], [7, 16], [8, 16], [9, 16], 
                          [10, 16], [11, 16], [12, 16], [13, 16], [1, 15], [2, 15], [3, 15], [4, 15], [5, 15], [6, 15], [7, 15], [8, 15], [9, 15], [10, 15], [11, 15], 
                          [12, 15], [13, 15], [0, 14], [1, 14], [2, 14], [3, 14], [4, 14], [5, 14], [6, 14], [7, 14], [8, 14], [9, 14], [10, 14], [11, 14], [12, 14], 
                          [13, 14]]
        
        right_locations = [[14, 27], [14, 26], [15, 26], [14, 25], [15, 25], [16, 25], [14, 24], [15, 24], [16, 24], [17, 24], [14, 23], [15, 23], [16, 23], [17, 23], 
                           [18, 23], [14, 22], [15, 22], [16, 22], [17, 22], [18, 22], [19, 22], [14, 21], [15, 21], [16, 21], [17, 21], [18, 21], [19, 21], [20, 21], 
                           [14, 20], [15, 20], [16, 20], [17, 20], [18, 20], [19, 20], [20, 20], [21, 20], [14, 19], [15, 19], [16, 19], [17, 19], [18, 19], [19, 19], 
                           [20, 19], [21, 19], [22, 19], [14, 18], [15, 18], [16, 18], [17, 18], [18, 18], [19, 18], [20, 18], [21, 18], [22, 18], [23, 18], [14, 17], 
                           [15, 17], [16, 17], [17, 17], [18, 17], [19, 17], [20, 17], [21, 17], [22, 17], [23, 17], [24, 17], [14, 16], [15, 16], [16, 16], [17, 16], 
                           [18, 16], [19, 16], [20, 16], [21, 16], [22, 16], [23, 16], [24, 16], [25, 16], [14, 15], [15, 15], [16, 15], [17, 15], [18, 15], [19, 15], 
                           [20, 15], [21, 15], [22, 15], [23, 15], [24, 15], [25, 15], [26, 15], [14, 14], [15, 14], [16, 14], [17, 14], [18, 14], [19, 14], [20, 14], 
                           [21, 14], [22, 14], [23, 14], [24, 14], [25, 14], [26, 14], [27, 14]]
        
        left_defenses = 0
        left_supports = 0
        right_defenses = 0
        right_supports = 0

        for location in left_locations:
            unit = game_state.contains_stationary_unit(location)
            if unit:
                if unit.unit_type != SUPPORT:
                    left_defenses += 1
                elif unit.unit_type == SUPPORT:
                    left_supports += 1
        for location in right_locations:
            unit = game_state.contains_stationary_unit(location)
            if unit:
                if unit.unit_type != SUPPORT:
                    right_defenses += 1
                elif unit.unit_type == SUPPORT:
                    right_supports += 1

        defense_side = None
        if left_defenses > right_defenses:
            defense_side = 'left'
        elif right_defenses > left_defenses:
            defense_side = 'right'
        else:
            defense_side = 'left'
        
        most_supports = None
        if left_supports > 2 * right_supports and left_supports > 2:
            most_supports = 'left'
        elif right_supports > 2 * left_supports and right_supports > 2:
            most_supports = 'right'

        return defense_side, most_supports
        

        
    def check_attack_side(self):
        side_most_attacked = None
        for location in self.scored_on_locations:
            if location[0] < 14:
                side_most_attacked = 'left'
            elif location[0] > 13 and location[0] < 28:
                side_most_attacked = 'right'
        return side_most_attacked


    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            if not path == None:
                for path_location in path:
                    # Get number of enemy turrets that can attack each location and multiply by turret damage
                    damage += len(game_state.get_attackers(path_location, 0)) * \
                        gamelib.GameUnit(TURRET, game_state.config).damage_i
                damages.append(damage)
        # Now just return the location that takes the least damage and damage amount
        return location_options[damages.index(min(damages))], min(damages)

    def least_damage_spawn_location(self, game_state, location_options):
        if not location_options:
            # Return None and infinite damage if no location options are provided
            return None, float('inf')

        damages = []
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            if path is None:
                # Assign infinite damage if path is None
                damages.append(float('inf'))
                continue

            damage = sum(len(game_state.get_attackers(path_location, 0)) *
                     gamelib.GameUnit(TURRET, game_state.config).damage_i for path_location in path)
            damages.append(damage)

        min_damage = min(damages)
        safest_location = location_options[damages.index(min_damage)]
        return safest_location, min_damage
    

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x=None, valid_y=None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units

    # returns all locations that are not blocked by stationary units
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called 
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at in json-docs.html in the root of the Starterkit.
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
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


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
