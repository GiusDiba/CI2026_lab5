from wumpus_world import Map
from entities import Wumpus, Gold, Adventurer, Pit

def standardWorld() -> Map:
    brd = Map(4, 4)
    brd.insertEntity(Pit(0, 3))
    brd.insertEntity(Wumpus(1, 0))
    brd.insertEntity(Gold(1 ,1))
    brd.insertEntity(Pit(1, 2))
    brd.insertEntity(Adventurer(3, 0))
    brd.insertEntity(Pit(3,2))
    return brd