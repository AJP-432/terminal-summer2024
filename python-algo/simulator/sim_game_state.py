from .sim_game_map import SimGameMap
from .constants import UnitType, MapEdges
import json
from game_configs import configs
from .sim_unit import *

class SimGameState:
    STRUCTURES = [UnitType.WALL, UnitType.TURRET, UnitType.SUPPORT]
    WALKERS = [UnitType.SCOUT, UnitType.DEMOLISHER, UnitType.INTERCEPTOR]

    def __init__(self, last_action_frame: json, test: json) -> None:
        self.frame = -1
        self.p1_units = []
        self.p2_units = []

        self.walker_stacks = set()
        self.supports = set()
        self.fighters = set()

        self.game_map = SimGameMap()
        self.pathfinder = SimShortestPath()

        self.parse_frame(last_action_frame)
        self.load_units(last_action_frame["p1Units"], last_action_frame["p2Units"], test)
        

    def parse_frame(self, frame: json) -> None:
        p1_health, p1_SP, p1_MP, p1_time = frame["p1Stats"][:3]
        p2_health, p2_SP, p2_MP, p2_time = frame["p2Stats"][:3]

        self.player_stats = [
            {
                "health": p1_health,
                "SP": p1_SP,
                "MP": p1_MP,
                "time": p1_time
            },
            {
                "health": p2_health,
                "SP": p2_SP,
                "MP": p2_MP,
                "time": p2_time
            }
        ]

    def load_units(self, p1_units: list, p2_units: list, test_units: json) -> None:
        # p1 and p2 units are going to be the type from the frame state. Tests will be our notation 
        # I think turrets and walls can just be SimUnit and don't need serparate derived classes
        # Supports and walkers have their own derived classes. 
        # I might have missed some properties in the above classes. Please verify
        pass

    
    def get_walkers(self) -> set:
        return self.walker_stacks
    
    def get_supports(self) -> set:
        return self.supports
    
    def get_fighters(self) -> set:
        return self.fighters

    def is_round_over(self) -> bool:
        return len(self.walker_stacks) == 0
    
    # TODO
    def get_results(self) -> list[str]:
        pass

    def contains_stationary_unit(self, xy: tuple[int, int]) -> bool:
        unit = self.game_map[xy]
        return unit is not None and unit.unit_type in self.STRUCTURES

    def find_path_to_edge(self, xy: tuple[int, int], target_edge: MapEdges) -> list[tuple[int, int]]:
        pass

    def run_frame(self) -> None:
        # all logic in a single loop iteration
        if self.is_round_over():
            return
        
        self.frame += 1

        # supports givign shields
        for support in self.supports:
            support_xy = support.x, support.y
            shield_range = self.game_map.get_locations_in_range(support_xy, support.shield_range)

            for xy in shield_range:
                unit = self.game_map[xy] # either None, stationary unit or walker stack 
                if unit and not self.contains_stationary_unit(xy):
                    if unit.player_index == support.player_index and unit not in support.given_shield:
                        support.given_shield.add(unit)
                        unit.health += support.shield_per_unit + support.shield_bonus_per_y * (support.y - xy[1])

        # move walkers
        have_moved = set()
        for walker_stack in self.walker_stacks:
            if walker_stack in have_moved:
                continue

            if self.frame % walker_stack.speed != 0:
                continue

            quadrant = self.game_map.get_quadrant(walker_stack.x, walker_stack.y)
            if (walker_stack.x, walker_stack.y) in self.game_map.get_edge_locations(quadrant):
                # remove walker_stack from map
                self.game_map.remove_unit(walker_stack.x, walker_stack.y)
                self.fighters.remove(walker_stack)
                self.walker_stacks.remove(walker_stack)

                # update resources
                enemy_index = 1 if walker_stack.player_index == 0 else 0
                self.player_stats[enemy_index]["health"] -= 2 if walker_stack.unit_type == UnitType.DEMOLISHER else 1
                self.player_stats[walker_stack.player_index]["SP"] += 2 if walker_stack.unit_type == UnitType.DEMOLISHER else 1
                continue

            # move unit to next spot in path. 
            # Assumption that there will be no other units in the path.
            next_step = walker_stack.next_step()
            self.game_map.remove_unit(walker_stack.x, walker_stack.y)
            self.game_map.add_unit(next_step, walker_stack)

        # attack
        units_to_remove = set()
        any_destoyed = False
        for fighter in self.get_fighters():
            # all units in walker stack attack individually. Also works for turrets
            for _ in range(fighter.unit_count):
                target = self.game_map.get_best_target(fighter)
                if not target:
                    continue
                
                target_health = target.inflict_damage(fighter.damage_structure if target.unit_type in self.STRUCTURES else fighter.damage_walker)
                if target_health <= 0:
                    units_to_remove.add(target)
                    any_destoyed = True

        

        