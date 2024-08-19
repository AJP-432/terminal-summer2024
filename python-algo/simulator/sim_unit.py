from queue import Queue
from typing import Literal
from pygame import display

from .constants import *
from .game_configs import configs

class SimUnit:
    def __init__(self, unit_type: UnitType, xy: tuple[int, int], player_index: Literal[0, 1], health: float = None, unit_count = 1) -> None:
        self.unit_count = unit_count
        self.unit_type = unit_type
        self.x, self.y = xy
        self.health = health or configs["unitInformation"][unit_type.value]["startHealth"]
        self.player_index = player_index
        self.upgraded = False
        self.cost = configs["unitInformation"][unit_type.value]["cost"]
        self.attackRange = configs["unitInformation"][unit_type.value].get("attackRange", 0)
        self.damage_structure = configs["unitInformation"][unit_type.value].get("attackDamageTower", 0)
        self.damage_walker = configs["unitInformation"][unit_type.value].get("attackDamageMobile", 0)
        # self.pending_removal = False
    
    def inflict_damage(self, damage: float) -> float:
        self.health -= damage
        return self.health
    
    def upgrade(self):
        if self.unit_type == UnitType.TURRET:
            self.attackRange = configs["unitInformation"][self.unit_type]["upgrade"]["attackRange"]
            self.damage_walker = configs["unitInformation"][self.unit_type]["upgrade"]["attackDamageMobile"]

    def draw(self, screen: display):
        pass

class SimSupport(SimUnit):
    def __init__(self, xy: tuple[int, int], player_index: Literal[0, 1],  health:int = None) -> None:
        super().__init__(UnitType.SUPPORT, xy, player_index, health)
        self.given_shield = set()
        self.shieldPerUnit = configs["unitInformation"][UnitType.SUPPORT.value]["shieldPerUnit"]
        self.shieldBonusPerY = configs["unitInformation"][UnitType.SUPPORT.value]["shieldBonusPerY"]
        self.shieldRange = configs["unitInformation"][UnitType.SUPPORT.value]["shieldRange"]
    
    def upgrade(self):
        self.shieldRange = configs["unitInformation"][UnitType.SUPPORT.value]["upgrade"]["shieldRange"]
        self.shieldPerUnit = configs["unitInformation"][self.unit_type]["upgrade"]["shieldPerUnit"]
        self.shieldBonusPerY = configs["unitInformation"][self.unit_type]["upgrade"]["shieldBonusPerY"]

class SimWalkerStack(SimUnit):
    def __init__(self, unit_type: UnitType, xy: tuple[int, int], player_index: Literal[0, 1], unit_count) -> None:
        super().__init__(unit_type, xy, player_index, unit_count)
        self.target_edge = self.get_target_edge()
        self.health = [configs["unitInformation"][unit_type.value]["startHealth"] for _ in range(unit_count)]
        self.path = Queue()
        self.speed = configs["unitInformation"][unit_type.value].get("speed", 0)

    def get_target_edge(self):
        if self.target_edge:
            return self.target_edge

        # hard coded half arena size
        return MapEdges.TOP_LEFT if self.x >= 14 else MapEdges.TOP_RIGHT        

    def set_path(self, path):
        self.path.queue.clear()
        for step in path: 
            self.path.put(step)

    def next_step(self):
        return tuple(self.path.get())
    
    def add_to_stack(self):
        self.unit_count += 1
        self.health.append(self.health[0])
    
    def inflict_damage(self, damage: float) -> float:
        """
        returns health of the last unit in the stack
        """
        if len(self.health) == 0:
            return 0
        
        self.health[-1] -= damage

        if self.health[-1] <= 0:
            self.unit_count -= 1
            return self.health.pop()
        
        return self.health[-1]
        



    