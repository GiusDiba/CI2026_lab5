from entities import Entity, Wumpus, FreeCell, Pit, Adventurer, Gold

class Cell():
    effects: set[str] 
    entities: list[Entity]
    symbol: str

    def __init__(self, entity: Entity):
        self.entities = [entity]
        self.effects = set(entity.getSideEffect()) if entity.getSideEffect() is not None else set()
        self.symbol = entity.symbol

    def addEffect(self, effect: str):
        self.effects.add(effect)

    def removeEffect(self, effect: str):
        self.effects.discard(effect)

class Map():

    shape: tuple[int]
    board: list[Cell]

    wumpus_list: list[Cell]
    pit_list: list[Cell]
    gold_list: list[Cell]
    

    # Initializes an empty board
    def __init__(self, width: int, height: int):
        self.shape = (width, height)
        self.board = [[ Cell(FreeCell(row, col)) for col in range(width)] for row in range(height)]

    def __str__(self) -> str:
        brd = ""
        for row in self.board:
            for item in row:
                brd += f"{item.symbol} "
            brd += "\n"

        return brd

    #def addWumpus(self, row, col):


