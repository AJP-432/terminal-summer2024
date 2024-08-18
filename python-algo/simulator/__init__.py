"""
The gamelib package contains modules that assist in algo creation \n

The GameState class in game_state.py is the main class most players interact with. 
It contains functions that let you get information about resources, deploy units, and help you strategize your move. \n

The GameMap class in game_map.py represents the current game map. It can be used to access information related to the locations of units. 
Investigating it is useful for any player that wants to access more information about the current state of the game. \n

The GameUnit class in unit.py represents a single unit. 
Investigating it is useful for any player that wants to access information about units. \n

The AlgoCore class in algocore.py handles communication with the game engine, and forms the bones of an algo. AlgoStrategy inherits from it. 
Investigating it is useful for advanced players interested in getting data from the action phase or communicating directly with the game engine. \n

The Navigation class in navigation.py contains functions related to path-finding, which are used by GameState in pathing related functions. 
Investigating it is useful for advanced player who want to optimize the slow default pathing algorithm we provide. \n 

util.py contains a small handful of functions that help with communication, including the debug-printing function, debug_write().
"""

from .main import Simulator
from .sim_game_state import SimGameState
from .sim_unit import SimGameUnit   
from .sim_game_map import SimGameMap
from .sim_navigation import SimNavigation

__all__ = ["simulator", "sim_game_state", "sim_game_map", "sim_navigation", "sim_unit"]
 