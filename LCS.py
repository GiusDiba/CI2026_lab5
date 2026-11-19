from __future__ import annotations
from dataclasses import dataclass
from entities import EnvironmentMessage, Directions, Adventurer, OppositeDirections
from enum import Enum
from wumpus_world import Map
from random import choice

@dataclass
class Classifier():
    condition: frozenset
    action: frozenset

    def matches(self, messages: set):
        return self.condition <= messages

### STARTING RULESET ###
# Rule #-1: I'm out {"END"}
#   => action: terminate, you won
# Rule #0: I found the exit
#   => action: If you have gold, exit (you won), else remember exit location
# Rule #1: I find gold
#   => action: take gold, if exit location is known, build ideal path to exit | JUST BACKTRACK FOR NOW
# Rule #2: I feel a bump
#   => action:  remove current facing direction as a possible action in this cell
#               add wall to memory
#               get available directions, rotate until an available direction is reached and then advance*
# Rule #3: I don't feel any breeze or stench
#   => action: advance
# Rule #4: I feel breeze
#   => action:
#               Add to the no-go list all directions which lead to non visited cells
#               get available directions, rotate until an available direction is reached and then advance*
# Rule 54: I feel stench
#   => action:  if I felt stench in two consecutive diagonal cells
#                   if I have arrows:
#                       rotate towards the middle and shoot
#                       Rule #4.1: I hear a scream:
#                           => action: add current facing direction as a possible action in this cell 
#               else:
#                    Add to the no-go list all directions which lead to non visited cells
#                   get available directions, rotate until an available direction is reached and then advance*
#
# * If I have gold, and I know the exit location, rebuild path and align to the next action 

### "helpers" ###

# TODO, in the meantime just backtrack
def buld_path_to_exit() -> list[Directions]:
    pass

def check_side(start: tuple[int], middle: tuple[int], end: tuple[int], adv: Adventurer, sensation: EnvironmentMessage):
    if (start in adv.memory.keys() and end in adv.memory.keys() and middle not in adv.memory.keys()):
        content_1 = adv.memory[start]
        content_2 = adv.memory[end]
        if sensation in content_1.felt and sensation in content_2.felt:
            return True

    return False

def find_legal_actions(can_move_to: set, wrld: Map) -> set:
    for direction, pos in wrld.adventurer.getAdjacent().items():
        if pos in wrld.adventurer.memory.keys():
            if not wrld.adventurer.memory[pos].isObstacle():
                can_move_to.add(direction)
        else:
            can_move_to.add(direction)
    return can_move_to

def rotate_and_move(can_move_to: set, wrld: Map):
    rotation_direction = choice(("left","right"))
    print(f"Legal directions: {can_move_to}")
    direction = choice(tuple(can_move_to))
    while wrld.adventurer.getFacingDirection() != direction:
        wrld.rotate(rotation_direction)
    print(f"Moving {wrld.adventurer.getFacingDirection()}")
    wrld.advance()

def find_prev_cell_visits(wrld: Map) -> int:
    adj = wrld.adventurer.getAdjacent()
    prev = wrld.adventurer.memory[adj[OppositeDirections[wrld.adventurer.getFacingDirection()].value]].visits_amt
    print(f"Previous cell visited {prev} times")
    return prev

### ALL ACTIONS ###

# 0
def exit_found(messages: set, wrld: Map, ariadnes_thread: list[Directions]) -> set:
    if wrld.adventurer.hasGold():
        return {LCSMessages.end.value}
    else:
        wrld.adventurer.exit_loc = wrld.adventurer.position
        ariadnes_thread = [wrld.adventurer.getFacingDirection()]
        env_messages = wrld.adventurer.sensations.copy()
        messages.add(LCSMessages.tracking.value)
        messages.discard(EnvironmentMessage.exit_loc.value)
        return messages

def tracking(messages: set, wrld: Map, ariadnes_thread: list[Directions]) -> set:
    ariadnes_thread.append([(OppositeDirections[wrld.adventurer.getFacingDirection()].value)])
    env_messages = wrld.adventurer.sensations.copy()
    messages.discard(LCSMessages.tracking.value)
    env_messages.discard(EnvironmentMessage.exit_loc.value)
    return messages.union(env_messages)

# 1
def gold_found(messages: set, wrld: Map, *_) -> set:
    pos = wrld.adventurer.position
    wrld.takeGold(pos[0], pos[1])
    wrld.adventurer.takeGold()
    env_messages = wrld.adventurer.sensations.copy()
    messages = env_messages
    messages.add(LCSMessages.gold.value)
    messages.add(LCSMessages.tracking.value)
    return messages.union(env_messages)

# 1.5 - If I have gold, I just have to backtrack
def got_gold(messages: set, wrld: Map, ariadnes_thread: list[Directions]) -> set:
    direction = ariadnes_thread.pop()
    rotate_and_move({direction}, wrld)
    env_messages = wrld.adventurer.sensations.copy()
    messages = env_messages
    return messages.union({LCSMessages.gold.value, LCSMessages.tracking.value})

# 2
def bump_advance(messages: set, wrld: Map, *_):
    adj = wrld.adventurer.getAdjacent()
    wrld.adventurer.addMemory(adj[wrld.adventurer.getFacingDirection()], True)
    can_move_to = find_legal_actions(set(), wrld)
    rotate_and_move(can_move_to, wrld)
    env_messages = wrld.adventurer.sensations.copy()
    messages = env_messages
    #messages.add(LCSMessages.tracking.value)
    return messages

# 3
def clear_advance(messages: set, wrld: Map, *_) -> set:
    wrld.advance()
    env_messages = wrld.adventurer.sensations.copy()
    messages = env_messages
    messages.add(LCSMessages.tracking.value)
    return messages

# 4
def breeze_advance(messages: set, wrld: Map, *_) -> set:
    if find_prev_cell_visits(wrld) > 1:
        can_move_to = find_legal_actions(set(), wrld)
    else:
        can_move_to = {OppositeDirections[wrld.adventurer.getFacingDirection()].value}
    rotate_and_move(can_move_to, wrld)
    env_messages = wrld.adventurer.sensations.copy()
    messages = env_messages
    messages.add(LCSMessages.tracking.value)
    return messages
    

# 5
def stench_advance(messages: set, wrld: Map, *_) -> set:
    adj = wrld.adventurer.getAdjacent()

    # If I have arrows, I can attempt to slay the wumpus
    if wrld.adventurer.hasArrows():
        sides = {
            Directions.north.value: {
                "middle": adj[Directions.north.value],
                "start": (adj[Directions.north.value][0], adj[Directions.north.value][1] - 1),
                "end": (adj[Directions.north.value][0], adj[Directions.north.value][1] + 1)
            },
            Directions.east.value: {
                "middle": adj[Directions.east.value],
                "start": (adj[Directions.east.value][0] -1, adj[Directions.east.value][1]),
                "end": (adj[Directions.east.value][0] + 1, adj[Directions.east.value][1])
            },
            Directions.south.value: {
                "middle": adj[Directions.north.value],
                "start": (adj[Directions.north.value][0], adj[Directions.north.value][1] - 1),
                "end": (adj[Directions.north.value][0], adj[Directions.north.value][1] + 1)
            },
            Directions.west.value: {
                "middle": adj[Directions.east.value],
                "start": (adj[Directions.east.value][0] -1, adj[Directions.east.value][1]),
                "end": (adj[Directions.east.value][0] + 1, adj[Directions.east.value][1])
            }
        }

        is_wumpus = False
        wumpus_direction = None
        for direction, side in sides.items():
            is_wumpus = check_side(side["start"], side["middle"], side["end"], wrld.adventurer, EnvironmentMessage.wumpus.value)
            if is_wumpus: # Try to slay wumpus
                wumpus_direction = direction

                while wrld.adventurer.getFacingDirection() != direction:
                    wrld.rotate("right")
                wrld.shoot()
                env_messages = wrld.adventurer.sensations.copy()
                # 
                # sub_rules = [
                #     screamRule, # The wumpus has been slain: I can safely go forward TODO
                #     clearRule,  # The wumpus is still alive: I can go forward, if there is no breeze
                #     breezeRule  # The wumpus is still alive, regular breeze rule
                # ]
# 
                # for rule in sub_rules:
                #     if rule.matches(messages):
                #         rule.action(wrld)
                #         return  
                return env_messages
    # Otherwise, I just do the same thing as the breezeRule
    if find_prev_cell_visits(wrld) > 1:
        can_move_to = find_legal_actions(set(), wrld)
    else:
        can_move_to = {OppositeDirections[wrld.adventurer.getFacingDirection()].value}
    rotate_and_move(can_move_to, wrld)
    env_messages = wrld.adventurer.sensations.copy()
    messages = env_messages
    messages.add(LCSMessages.tracking.value)
    return messages

def terminate(*_):
    return {LCSMessages.end.value}

### RULES ###

# Messages generated by the classifier
class LCSMessages(Enum):
    end = "END"
    #known = "EXIT_KNOWN"
    gold = "GOLD"
    tracking = "TRACKING"

class LCS():

    deathRule = Classifier(
        condition = {EnvironmentMessage.death.value},
        action = terminate
    )

    terminateRule = Classifier(
        condition = {LCSMessages.end.value},
        action =  terminate
    )
    
    exitRule = Classifier(
        condition = {EnvironmentMessage.exit_loc.value},
        action = exit_found
    )
    
    trackRule = Classifier(
        condition = {LCSMessages.tracking.value},
        action = tracking
    )
    
    foundGoldRule = Classifier(
        condition = {EnvironmentMessage.gold.value},
        action = gold_found
    )
    
    gotGoldBacktrackRule = Classifier(
        condition = {LCSMessages.gold.value, LCSMessages.tracking.value},
        action = got_gold
    )

    #gotGoldRule = Classifier = Classifier(
    #    condition = {LCSMessages.gold.value}
    #)
    
    heardScreamRule = Classifier(
        condition = {EnvironmentMessage.scream.value},
        action = clear_advance
    )
    
    bumpRule = Classifier (
        condition = {EnvironmentMessage.wall.value},
        action = bump_advance
    )
    
    stenchRule = Classifier(
        condition = {EnvironmentMessage.wumpus.value},
        action = stench_advance
    )
    
    breezeRule = Classifier(
        condition = {EnvironmentMessage.pit.value},
        action = breeze_advance
    )
    
    noDangersRule = Classifier(
        condition = set(),
        action = clear_advance
    )

    wrld: Map
    ruleset: list[Classifier]
    message_bucket: set
    ariadnes_thread: list[Directions]

    def __init__(self, wrld: Map):
        self.ruleset = [
            self.deathRule,
            self.terminateRule,
            self.exitRule,
            self.foundGoldRule,
            self.gotGoldBacktrackRule,
            #self.gotGoldRule,
            self.heardScreamRule,
            self.trackRule,
            self.bumpRule,
            self.stenchRule,
            self.breezeRule,
            self.noDangersRule
        ]
        self.ariadnes_thread = []
        self.wrld = wrld
        self.message_bucket = wrld.adventurer.sensations.copy()
        print("ALL CONDITIONS:")
        for rule in self.ruleset:
            print(f"{self.ruleset.index(rule)}: {rule.condition}")

    def singleStep(self):
        print(f"MESSAGE BUCKET: {self.message_bucket}")
        for rule in self.ruleset:
            if rule.matches(self.message_bucket):
                print(f"APPLYING RULE: {self.ruleset.index(rule)} => {rule.condition}")
                self.message_bucket = rule.action(self.message_bucket, self.wrld, self.ariadnes_thread)
                print(f"MESSAGE BUCKET IS NOW: {self.message_bucket}")
                return

    def runLCS(self):
        actions = 1
        while not self.terminateRule.matches(self.message_bucket):
            print(f"=== ACTION {actions} ===")
            self.singleStep()
            actions += 1
        