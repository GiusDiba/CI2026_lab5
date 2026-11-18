from __future__ import annotations
from collections import deque
from enum import Enum

class EnvironmentMessage(Enum):
    wumpus = "stench"
    pit = "breeze"
    gold = "glitter"
    start = "at_start"
    scream = "scream"
    wall = "bump"
    adventurer = None
    free = None

class MovesEffects(Enum):
    north = (-1, 0)
    south = (+1, 0)
    east = (0, +1)
    west = (0, -1)

class Directions(Enum):
    north = "north" 
    south = "south"
    east = "east"
    west = "west"

class Entity():
    name: str
    position: tuple
    side_effect: str
    symbol: str

    def __init__(self, name: str, row: int, col:int):
        self.name = name
        self.position = (row,col)
        self.side_effect = EnvironmentMessage[name].value

    def __str__(self) -> str:
        return f"{self.name}: in {self.position[0]},{self.position[1]}"

    def getSideEffect(self) -> str:
        return self.side_effect

class Wumpus(Entity):
    def __init__(self, row: int, col: int):
        super().__init__("wumpus", row, col)
        self.symbol = "W"

class Pit(Entity):
    def __init__(self, row: int, col: int):
        super().__init__("pit", row, col)
        self.symbol = "O"

class FreeCell(Entity):
    def __init__(self, row: int, col: int):
        super().__init__("free", row, col)
        self.symbol = "."

class Gold(Entity):
    def __init__(self, row: int, col: int):
        super().__init__("gold", row, col)
        self.symbol = "G"

class ProximitySensations():
    nearby_effects: dict
    dangerous: bool
    legal_moves = set[Directions]

    def __init__(self, danger: bool = False):
        self.nearby_effects = {
            Directions.north.value: set(),
            Directions.south.value: set(),
            Directions.east.value: set(),
            Directions.west.value: set()
        }
        self.legal_moves = {Directions.north.value, Directions.south.value, Directions.east.value, Directions.west.value}
        self.dangerous = danger

    def __str__(self) -> str:
        st = "\n"
        for k in self.nearby_effects:
            st += f"\t{k}: {self.nearby_effects[k]}\n"
        return st

    def setDanger(self, danger: bool):
        self.dangerous = danger

    def discardLegalMove(self, move: Directions):
        self.legal_moves.discard(move)

    def addNearbyEffects(self, direction: Directions, effects: set[EnvironmentMessage]):
        self.nearby_effects[direction] = self.nearby_effects[direction].union(effects)


class Adventurer(Entity):

    arrows_amt: int
    facing: deque
    sensations: set
    memory: dict[ProximitySensations]

    def __init__(self, row: int, col: int, arrows: int = 1, facing: str = "north"):
        super().__init__("adventurer", row, col)
        self.arrows_amt = arrows
        self.symbol = "^"
        self.sensations = set()

        # The actual direction the adventurer is facing is the one at index 0
        self.facing = deque([("north", "^"),("east", ">"),("south", "v"),("west", "<")])
        start_state = ProximitySensations()
        self.memory = {(row, col): start_state}

    def __str__(self) -> str:
        return super().__str__() + f" facing {self.facing[0]}"

    def advance(self) -> None:
        effects = MovesEffects[self.facing[0][0]].value
        self.position = (self.position[0] + effects[0], self.position[1] + effects[1])

    def getFacingDirection(self) -> str:
        return self.facing[0][0]

    def rotate(self, direction: str):
        if direction == "right":
            self.facing.rotate(-1)
        elif direction == "left":
            self.facing.rotate(1)
        else:
            return
        self.symbol = self.facing[0][1]
        
    def shoot(self) -> None:
        if self.arrows_amt > 0:
            self.arrows_amt -= 1

    def setSensations(self, sensations: set) -> None:
        self.sensations = sensations

    def addMemory(self, position: tuple[int]) -> None:
        self.memory[position] = ProximitySensations()

    def isNewMemory(self, position: tuple[int]) -> bool:
        if position in self.memory.keys():
            return False
        return True

    def memorizeCloseSensations(self, position: tuple[int], direction: Directions, sensations: set[EnvironmentMessage]):
        self.memory[position].addNearbyEffects(direction, sensations)

    def updateCurrentCloseSensation(self, old_sensations: set[EnvironmentMessage]) -> None:
        self.memorizeCloseSensations(self.position, self.facing[2][0], old_sensations)

    def addSensation(self, sensation: EnvironmentMessage) -> None:
        self.sensations.add(EnvironmentMessage.wall.value)

    def printMemory(self) -> None:
        for k in self.memory:
            print(f"{k}: {self.memory[k].__str__()}")
