import json

from pygame import display
from .sim_game_map import SimGameMap
from .sim_navigation import SimShortestPathFinder
from .constants import UnitType, MapEdges
from .game_configs import configs
from .sim_unit import SimUnit, SimSupport, SimWalkerStack

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
        self.all_units = set()

        self.game_map = SimGameMap()
        self.pathfinder = SimShortestPathFinder()

        self.parse_frame(last_action_frame)

        # merge arrays of units
        p1_units = [a+b for a,b in zip(last_action_frame["p1Units"], test["p1Units"])]
        p2_units = [a+b for a,b in zip(last_action_frame["p2Units"], test["p2Units"])]

        # self.load_units(p1_units, p2_units)
        
    """
    {
        "p1Units": [[] for _ in range(8)],
        "p2Units": [[] for _ in range(8)], 
    }
    """
    def parse_frame(self, frame: json) -> None:
        p1_health, p1_SP, p1_MP = frame["p1Stats"][:3]
        p2_health, p2_SP, p2_MP = frame["p2Stats"][:3]

        self.player_stats = [
            {
                "health": p1_health,
                "SP": p1_SP,
                "MP": p1_MP
            },
            {
                "health": p2_health,
                "SP": p2_SP,
                "MP": p2_MP
            }
        ]
            

    def load_units(self, p1_units: list[list], p2_units: list[list]) -> None:
        #TODO: Add each unit to self.all_units
        
        # Wall
        for entry in p1_units[0]:
            x = entry[0]
            y = entry[1]
            hp = entry[2]
            u = SimUnit(UnitType.WALL, (x, y), 0, hp)
            self.game_map.add_unit((x, y), u)

        for entry in p2_units[0]:
            x = entry[0]
            y = entry[1]
            hp = entry[2]
            u = SimUnit(UnitType.WALL, (x, y), 1, hp)
            self.game_map.add_unit((x, y), u)
        
        # Supports
        print("p1", p1_units)
        print("p2", p2_units)
        for entry in p1_units[1]:
            x = entry[0]
            y = entry[1]
            hp = entry[2]
            u = SimSupport((x, y), 0, hp)
            self.game_map.add_unit((x, y), u)
            self.supports.add(u)

        for entry in p2_units[1]:
            x = entry[0]
            y = entry[1]
            hp = entry[2]
            u = SimSupport((x, y), 1, hp)
            self.game_map.add_unit((x, y), u)
            self.supports.add(u)
        
        # Turret
        for entry in p1_units[2]:
            x = entry[0]
            y = entry[1]
            hp = entry[2]
            u = SimUnit(UnitType.TURRET, (x, y), 0, hp)
            self.game_map.add_unit((x, y), u)
            self.fighters.add(u)

        for entry in p2_units[2]:
            x = entry[0]
            y = entry[1]
            hp = entry[2]
            u = SimUnit(UnitType.TURRET, (x, y), 1, hp)
            self.game_map.add_unit((x, y), u)
            self.fighters.add(u)
        
        # Scout & Demo & Interceptor
        for i in range(3, 6):
            for entry in p1_units[i]:
                x = entry[0]
                y = entry[1]
                unit = self.game_map[x, y]
                if not unit:
                    u = SimWalkerStack(i, (x, y), 0, 1)
                    self.game_map.add_unit((x, y), u)
                    self.fighters.add(u)
                    self.walker_stacks.add(u)
                else: 
                    unit.add_to_stack()

            for entry in p2_units[i]:
                x = entry[0]
                y = entry[1]
                if not unit:
                    u = SimWalkerStack(i, (x, y), 1, 1)
                    self.game_map.add_unit((x, y), u)
                    self.fighters.add(u)
                    self.walker_stacks.add(u)
                else: 
                    unit.add_to_stack()
                
        # Upgrades
        for x, y, _, _ in p1_units[7]:
            self.game_map[x, y].upgrade()

        for x, y, _, _ in p2_units[7]:
            self.game_map[x, y].upgrade()
        
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

    def draw(self, screen: display) -> None:
        # draw map
        self.game_map.draw(screen)
        # draw units
        for unit in self.all_units:
            unit.draw(screen)

    def run_frame(self) -> None:
        # all logic in a single loop iteration
        if self.is_round_over():
            return
        
        self.frame += 1

        # supports giving shields
        for support in self.supports:
            support_xy = support.x, support.y
            shield_range = self.game_map.get_locations_in_range(support_xy, support.shield_range)

            for xy in shield_range:
                unit = self.game_map[xy] # either None, stationary unit or walker stack 
                if unit and not self.contains_stationary_unit(xy):
                    if unit.player_index == support.player_index and unit not in support.given_shield:
                        support.given_shield.add(unit)
                        unit.health = list(map(lambda x: x + support.shield_per_unit, unit.health))

        # move walkers
        have_moved = set()
        for walker_stack in self.walker_stacks:
            if walker_stack in have_moved or self.frame % walker_stack.speed != 0:
                continue

            quadrant = self.game_map.get_quadrant(walker_stack.x, walker_stack.y)
            if (walker_stack.x, walker_stack.y) in self.game_map.get_edge_locations(quadrant):
                # remove walker_stack from map
                self.game_map.remove_unit(walker_stack.x, walker_stack.y)
                self.fighters.remove(walker_stack)
                self.all_units.remove(walker_stack)
                self.walker_stacks.remove(walker_stack)

                # update resources
                enemy_index = 1 if walker_stack.player_index == 0 else 0
                damage = walker_stack.unit_count * (2 if walker_stack.unit_type == UnitType.DEMOLISHER else 1)
                self.player_stats[enemy_index]["health"] -= damage
                self.player_stats[walker_stack.player_index]["SP"] += damage
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
                    if target.unit_type in [UnitType.WALL, UnitType.TURRET, UnitType.SUPPORT]:
                        any_destoyed = True
                        units_to_remove.add(target)
                    
                    elif target.unit_count <= 0: 
                        units_to_remove.add(target)
        
        if any_destoyed:
            for walker_stack in self.walker_stacks:
                if walker_stack in units_to_remove:
                    continue
                
                # can be optimized 
                start_location = walker_stack.x, walker_stack.y
                edge_squares = self.game_map.get_edge_locations(walker_stack.get_target_edge())
                path = self.pathfinder.navigate_multiple_endpoints(start_location, edge_squares, self.game_state)
                walker_stack.set_path(path)


        # remove deleted units
        for unit in units_to_remove:
            self.game_map.remove_unit(unit.x, unit.y)
            if unit.unit_type in [UnitType.TURRET, UnitType.SCOUT, UnitType.DEMOLISHER, UnitType.INTERCEPTOR]:
                self.fighters.remove(unit)
                self.all_units.remove(unit)
                if unit.unit_type != UnitType.TURRET:
                    self.walker_stacks.remove(unit)

        

        

