from entities import Entity, Wumpus, FreeCell, Pit, Adventurer, Gold, EnvironmentMessage

class Cell():
    effects: dict
    entities: list[Entity]
    symbol: str

    def __init__(self, entity: Entity):
        self.entities = [entity]
        self.effects = {}
        if entity.getSideEffect() is not None:
            self.effects[entity.getSideEffect()] = 1
        self.symbol = entity.symbol

    def addEffect(self, effect: str) -> None:
        if effect in self.effects.keys():
            self.effects[effect] += 1
        else:
            self.effects[effect] = 1

    def removeEffect(self, effect: str, amt: int = 1) -> None:
        if effect in self.effects.keys():
            self.effects[effect] -= amt

    def addEntity(self, entity: Entity) -> None:
        self.entities.append(entity)
        self.symbol = entity.symbol
        if entity.getSideEffect() is not None:
            self.addEffect(entity.getSideEffect())

    def removeEntities(self, entity_type: type, max_ent: int = 1) -> list[Entity]:
        idx = []
        removed = []
        for i, e in enumerate(self.entities):
            if isinstance(e, entity_type):
                idx.append(i)
        if len(idx) != 0:
            count = 0
            for i in idx:
                while count < max_ent:
                    popped = self.entities.pop(i)
                    removed.append(popped)
                    count += 1
                    if count == len(idx):
                        self.removeEffect(popped.getSideEffect())
                        break

        self.symbol = self.entities[-1].symbol
        return removed

    def updateCellSymbol(self):
        self.symbol = self.entities[-1].symbol
        


class Map():

    shape: tuple[int]
    board: list[Cell]

    wumpus_list: list[Cell]
    pit_list: list[Cell]
    gold_list: list[Cell]
    adventurer: Adventurer
    

    # Initializes an empty board
    def __init__(self, width: int, height: int):
        self.shape = (width, height)
        self.board = [[ Cell(FreeCell(row, col)) for col in range(width)] for row in range(height)]
        self.wumpus_list = []
        self.pit_list = []
        self.gold_list = []

    def __str__(self) -> str:
        brd = ""
        for row in self.board:
            for item in row:
                brd += f"{item.symbol} "
            brd += "\n"

        return brd

    def insertEntity(self, entity: Entity) -> None:
        row, col = entity.position
        self.board[row][col].addEntity(entity)
        if isinstance(entity, Wumpus) or isinstance(entity, Pit):
            for idx in {-1, 1}:
                if row + idx >= 0 and row + idx < self.shape[1]:
                    self.board[row + idx][col].addEffect(entity.getSideEffect())
                if col + idx >= 0 and col + idx < self.shape[0]:
                    self.board[row][col + idx].addEffect(entity.getSideEffect())

    def removeEntities(self, entity: type, row: int, col: int, amt: int = 1) -> list[Entity]:
        removed = self.board[row][col].removeEntities(entity)
        amt_removed = len(removed)
        if amt_removed > 0:
            ent = removed[0]
            if isinstance(ent, Wumpus) or isinstance(ent, Pit):
                for idx in {-1, 1}:
                    if row + idx >= 0 and row + idx < self.shape[1]:
                        self.board[row + idx][col].removeEffect(ent.getSideEffect(), amt_removed)
                    if col + idx >= 0 and col + idx < self.shape[0]:
                        self.board[row][col + idx].removeEffect(ent.getSideEffect(), amt_removed)
        return removed

    def addAdventurer(self, row: int = 3, col: int = 0, arrows: int = 1, facing: str = "north"):
        adv = Adventurer(row, col, arrows, facing)
        self.insertEntity(adv)
        self.adventurer = adv
    
    def addPit(self, row: int, col: int):
        pit = Pit(row, col)
        self.insertEntity(Pit(row, col))
        self.pit_list.append(pit)

    def addWumpus(self, row: int, col: int):
        wum = Wumpus(row, col)
        self.insertEntity(wum)
        self.wumpus_list.append(wum)

    def addGold(self, row: int, col: int):
        gld = Gold(row, col)
        self.insertEntity(gld)
        self.gold_list.append(gld)

    def takeGold(self, row: int, col: int):
        removed = self.removeEntities(Gold, row, col)
        for r in removed:
            self.gold_list.remove(r)

    def slayWumpus(self, row: int, col: int):
        wum = self.removeEntities(Wumpus, row, col)
        if len(wum) != 0:
            for w in wum:
                self.wumpus_list.remove(w)
                [[ cell.addEffect(EnvironmentMessage.scream.value) for cell in row] for row in self.board]

    def advance(self) -> None:
        old_pos = self.adventurer.position
        self.adventurer.advance()

        self.removeEntities(Adventurer, old_pos[0], old_pos[1])
        self.insertEntity(self.adventurer)

    def rotate(self, direction: str) -> None:
        adv = self.adventurer
        adv.rotate(direction)
        self.board[adv.position[0]][adv.position[1]].updateCellSymbol()


