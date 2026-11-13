from collections import deque

NAMES_MAP = {
    "wumpus": "stench",
    "pit": "breeze",
    "gold": "glitter",
    "free": None,
    "adventurer": None
}

MOVES_EFFECTS = {
    "north": (-1, 0),
    "south": (+1, 0),
    "east": (0, +1),
    "west": (0, -1)
}

class Entity():
    name: str
    position: tuple
    side_effect: str

    def __init__(self, name: str, row: int, col:int):
        self.name = name
        self.position = (row,col)
        self.side_effect = NAMES_MAP[name]

    def __str__(self) -> str:
        return f"{self.name}: in {self.position[0]},{self.position[1]}"

class Wumpus(Entity):
    def __init__(self, row: int, col: int):
        super().__init__("wumpus", row, col)

class Pit(Entity):
    def __init__(self, row: int, col: int):
        super().__init__("pit", row, col)

class FreeCell(Entity):
    def __init__(self, row: int, col: int):
        super().__init__("free", row, col)

class Adventurer(Entity):

    arrows_amt: int
    facing: deque

    def __init__(self, row: int, col: int, arrows: int, facing: str = "north"):
        super().__init__("adventurer", row, col)
        self.arrows_amt = arrows

        # The actual direction the adventurer is facing is the one at index 0
        self.facing = deque(["north","east","south","west"])

    def __str__(self) -> str:
        return super().__str__() + f" facing {self.facing[0]}"

    def advance(self) -> None:
        effects = MOVES_EFFECTS[self.facing[0]]
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

