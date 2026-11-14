from wumpus_world import Map
from entities import Wumpus, Gold, Adventurer, Pit

def standardWorld() -> Map:
    brd = Map(4, 4)
    brd.addPit(0, 3)
    brd.addWumpus(1, 0)
    brd.addGold(1 ,1)
    brd.addPit(1, 2)
    brd.addAdventurer(3, 0)
    brd.addPit(3,2)
    return brd