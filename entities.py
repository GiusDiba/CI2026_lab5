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
        self.symbol = "#"

class Adventurer(Entity):

    arrows_amt: int
    facing: deque

    def __init__(self, row: int, col: int, arrows: int, facing: str = "north"):
        super().__init__("adventurer", row, col)
        self.arrows_amt = arrows
        self.symbol = "A"

        # The actual direction the adventurer is facing is the one at index 0
        self.facing = deque(["north","east","south","west"])

    def __str__(self) -> str:
        return super().__str__() + f" facing {self.facing[0]}"

    def advance(self) -> None:
        effects = MovesEffects[self.facing[0]].value
        self.position = (self.position[0] + effects[0], self.position[1] + effects[1])

    def getFacingDirection(self) -> str:
        return self.facing[0]

    def rotate(self, direction: str):
        if direction == "right":
            self.facing.rotate(-1)
        elif direction == "left":
            self.facing.rotate(1)
        else:
            return
        
    def shoot(self) -> None:
        if self.arrows_amt > 0:
            self.arrows_amt -= 1

class Gold(Entity):
    def __init__(self, row: int, col: int):
        super().__init__("gold", row, col)
