import math
from .constants import MapEdges, UnitType
from .sim_unit import *

class SimGameMap:
    edges = MapEdges
    ARENA_SIZE = 28
    HALF_ARENA = 14

    def __init__(self) -> None:
        self.map = [[None for _ in range(self.width)] for _ in range(self.height)]

    def __getitem__(self, key: tuple[int, int]) -> SimUnit | None:
        return self.map[key[0]][key[1]]
    
    def __setitem__(self, key: tuple[int, int], unit: SimUnit) -> None:
        self.map[key[0]][key[1]] = unit

    def is_in_bounds(self, x: int, y: int) -> bool:
        """Checks if the given location is inside the diamond shaped game board.

        Args:
            location: A map location

        Returns:
            True if the location is on the board, False otherwise
        
        """
        half_board = self.HALF_ARENA

        row_size = y + 1
        startx = half_board - row_size
        endx = startx + (2 * row_size) - 1
        top_half_check = (y < self.HALF_ARENA and x >= startx and x <= endx)

        row_size = (self.ARENA_SIZE - 1 - y) + 1
        startx = half_board - row_size
        endx = startx + (2 * row_size) - 1
        bottom_half_check = (y >= self.HALF_ARENA and x >= startx and x <= endx)

        return bottom_half_check or top_half_check

    def get_quadrant(self, x: int, y: int) -> MapEdges:
        if x < self.SIZE // 2 and y < self.SIZE // 2:
            return self.edges.BOTTOM_LEFT
        if x >= self.SIZE // 2 and y < self.SIZE // 2:
            return self.edges.BOTTOM_RIGHT
        if x >= self.SIZE // 2 and y >= self.SIZE // 2:
            return self.edges.TOP_RIGHT
        if x < self.SIZE // 2 and y >= self.SIZE // 2:
            return self.edges.TOP_LEFT

    def get_edge_locations(self, quadrant: MapEdges) -> list[tuple[int, int]]:
        return self.get_edges()[quadrant.value]

    def get_edges(self) -> list[list[tuple[int, int]]]:

        """Gets all of the edges and their edge locations

        Returns:
            A list with four lists inside of it of locations corresponding to the four edges.
            [0] = top_right, [1] = top_left, [2] = bottom_left, [3] = bottom_right.
        """
        # assume 0,0 is bottom left
        top_right = []
        for num in range(0, self.HALF_ARENA):
            x = self.HALF_ARENA + num
            y = self.ARENA_SIZE - 1 - num
            top_right.append([int(x), int(y)])
        top_left = []
        for num in range(0, self.HALF_ARENA):
            x = self.HALF_ARENA - 1 - num
            y = self.ARENA_SIZE - 1 - num
            top_left.append([int(x), int(y)])
        bottom_left = []
        for num in range(0, self.HALF_ARENA):
            x = self.HALF_ARENA - 1 - num
            y = num
            bottom_left.append([int(x), int(y)])
        bottom_right = []
        for num in range(0, self.HALF_ARENA):
            x = self.HALF_ARENA + num
            y = num
            bottom_right.append([int(x), int(y)])
        return [top_right, top_left, bottom_left, bottom_right]
    
    def distance_between_locations(self, location_1: tuple[int, int], location_2: tuple[int, int]) -> float:
        """Euclidean distance

        Args:
            location_1: An arbitrary location, [x, y]
            location_2: An arbitrary location, [x, y]

        Returns:
            The euclidean distance between the two locations

        """
        x1, y1 = location_1
        x2, y2 = location_2

        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
    #TODO:
    def distance_to_closest_edge(self, x: int, y: int) -> float:
        pass

    def add_unit(self, xy: tuple[int, int], unit: SimUnit | SimSupport | SimWalkerStack) -> None:
        self.map[xy[1]][xy[0]] = unit

    def remove_unit(self, x, y) -> None:
        if not self.is_in_bounds(x, y):
            return
        self.map[y][x] = None

    def get_locations_in_range(self, location: tuple[int, int], radius: float) -> list[tuple[int, int]]:
        """Gets locations in a circular area around a location

        Args:
            location: The center of our search area
            radius: The radius of our search area

        Returns:
            The locations that are within our search area

        """
        if radius < 0 or radius > self.ARENA_SIZE:
            self.warn("Radius {} was passed to get_locations_in_range. Expected integer between 0 and {}".format(radius, self.ARENA_SIZE))
        if not self.is_in_bounds(location):
            self._invalid_coordinates(location)

        x, y = location
        locations = []
        search_radius = math.ceil(radius)
        getHitRadius = 0.01 #from the configs
        for i in range(int(x - search_radius), int(x + search_radius + 1)):
            for j in range(int(y - search_radius), int(y + search_radius + 1)):
                new_location = (i, j)
                # A unit with a given range affects all locations whose centers are within that range + get hit radius
                if self.is_in_bounds(new_location) and self.distance_between_locations(location, new_location) < radius + getHitRadius:
                    locations.append(new_location)
        return locations
    
    def get_best_target(self, unit: SimUnit): 
        visible_locations = self.get_locations_in_range(tuple(unit.x, unit.y), unit.attackRange)
        best_target_location = visible_locations[0]

        for xy in visible_locations: 
            # None or SimUnit/derived classes
            target = self[xy]

            # No unit at this location
            if not target:
                continue

            # Don't target your own units
            if target.player_index == unit.player_index:
                continue

            # stationary units can't target other stationary units
            if unit.unit_type == UnitType.TURRET and target.unit_type in [UnitType.WALL, UnitType.TURRET, UnitType.SUPPORT]:
                continue

            # 1. Priority Targeting
            # NOTE: This won't happen because we aren't simulating opponent walkers
            # if best_target_location.unit_type in [WALL, SUPPORT, TURRET] and target.unit_type in [SCOUT, DEMOLISHER, INTERCEPTOR]:
            #     best_target_location = tuple(target.x, target.y)

            # 2. Distance Targeting
            if self.distance_between_locations(tuple(unit.x, unit.y), xy) < self.distance_between_locations(tuple(unit.x, unit.y), best_target_location):
                best_target_location = tuple(target.x, target.y)
                
            # 3. Health Targeting
            if target.health < best_target_location.health:
                best_target_location = tuple(target.x, target.y)
                
            # 4. Furthest into Your Side (Assume your side is the bottom)
            if target.y < best_target_location.y:
                best_target_location = tuple(target.x, target.y)

            # 5. Closest to an Edge
            if self.distance_to_closest_edge(target.x, target.y) < self.distance_to_closest_edge(best_target_location):
                best_target_location = tuple(target.x, target.y)
            
        return self[best_target_location]