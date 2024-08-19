from queue import Queue
from typing import Literal

from .constants import UnitType, MapEdges
from .constants import *
from game_configs import configs

class SimUnit:
    def __init__(self, unit_type: UnitType, xy: tuple[int, int], player_index: Literal[0, 1], health: float = None, unit_count = 1) -> None:
        self.unit_count = unit_count
        self.unit_type = unit_type
        self.x, self.y = xy
        self.health = health or configs["unitInformation"][unit_type]["startHealth"]
        self.player_index = player_index
        self.upgraded = False
        self.cost = configs["unitInformation"][unit_type]["cost"]
        self.attackRange = configs["unitInformation"][unit_type].get("attackRange", 0)
        self.damage_structure = configs["unitInformation"][unit_type].get("attackDamageTower", 0)
        self.damage_walker = configs["unitInformation"][unit_type].get("attackDamageMobile", 0)
        # self.pending_removal = False
    
    def inflict_damage(self, damage: float) -> float:
        self.health -= damage
        return self.health

class SimSupport(SimUnit):
    def __init__(self, xy: tuple[int, int], player_index: Literal[0, 1],  health:int = None) -> None:
        super().__init__(UnitType.SUPPORT, xy, player_index, health)
        self.given_shield = set()
        self.shieldPerUnit = configs["unitInformation"][UnitType.SUPPORT]["shieldPerUnit"]
        self.shieldBonusPerY = configs["unitInformation"][UnitType.SUPPORT]["shieldBonusPerY"]
        self.shieldRange = configs["unitInformation"][UnitType.SUPPORT]["shieldRange"]


class SimWalkerStack(SimUnit):
    def __init__(self, unit_type: UnitType, xy: tuple[int, int], player_index: Literal[0, 1], unit_count) -> None:
        super().__init__(unit_type, xy, player_index, unit_count)
        self.targetted_edge = None
        self.health = [configs["unitInformation"][unit_type]["startHealth"] for _ in range(unit_count)]
        self.path = Queue()
        self.speed = configs["unitInformation"][unit_type].get("speed", 0)
        

    def set_path(self, path):
        self.path.queue.clear()
        for step in path: 
            self.path.put(step)

    def next_step(self):
        return tuple(self.path.get())
    
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
        





    