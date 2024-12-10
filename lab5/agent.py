#
# ENSICAEN
# École Nationale Supérieure d'Ingénieurs de Caen
# 6 Boulevard Maréchal Juin
# F-14050 Caen Cedex France
#
# Artificial Intelligence 2I1AE1
#

#
# @file agents.py
#
# @author Régis Clouard.
#

from __future__ import print_function
import random
import copy
import sys
import utils


class Agent:
    """
    The base class for various flavors of the agent.
    This an implementation of the Strategy design pattern.
    """

    isLearningAgent = False

    def init(self, gridSize):
        raise Exception("Invalid Agent class, init() not implemented")

    def think(self, percept, action, score, isTraining=False):
        raise Exception("Invalid Agent class, think() not implemented")


def pause(text):
    if sys.version_info.major >= 3:
        input(text)
    else:
        raw_input(text)


class DummyAgent(Agent):
    """
    An example of simple Wumpus hunter brain: acts randomly...
    """

    def init(self, gridSize):
        pass

    def think(self, percept, action, score, isTraining=False):
        return random.choice(["shoot", "grab", "left", "right", "forward", "forward"])


class HumanAgent(Agent):
    """
    Game version using keyboard to control the agent
    """

    def init(self, gridSize):
        self.state = State(gridSize)
        self.isStarted = False

    def think(self, percept, action, score):
        """
        Returns the best action regarding the current state of the game.
        Available actions are ['left', 'right', 'forward', 'shoot', 'grab', 'climb'].
        """
        if not self.isStarted:
            self.isStarted = True
            return GRAB
        else:
            self.state.updateStateFromPercepts(percept, score)
            self.state.printWorld()
            key = input("Choose action (l, r, f, s, g, c) ? ")
            if key == "r":
                action = RIGHT
            elif key == "f":
                action = FORWARD
            elif key == "c":
                action = CLIMB
            elif key == "s":
                action = SHOOT
            elif key == "g":
                action = GRAB
            else:
                action = LEFT
            self.state.updateStateFromAction(action)
            return action


#######
####### Exercise: Rational Agent
#######
class RationalAgent(Agent):
    """
    Your smartest Wumpus hunter brain.
    """

    def init(self, gridSize):
        self.state = State(gridSize)
        " *** YOUR CODE HERE ***"
        self.isStarted = False

    def think(self, percept, action, score):
        """
        Returns the best action regarding the current state of the game.
        Available actions are ['left', 'right', 'forward', 'shoot', 'grab', 'climb'].


        state <- updateStateFromPercepts(percept)
        action <- bestAction(state)
        state <- updateStateFromAction(action)
        return action
        """

        # self.state.updateStateFromPercepts(percept, score)
        # bestAction = self.bestAction()
        # self.state.updateStateFromAction(bestAction)
        # return bestAction

        # function REFLEX-AGENT(percept) returns an action
        # static: rules, a set of condition—action rules
        # state ← INTERPRET-PERCEPTS(percept)
        # action ← CHOOSE-BEST-ACTION(state, rules)
        # return action
        if not self.isStarted:
            self.isStarted = True
            return GRAB
        else:
            self.state.updateStateFromPercepts(percept, score)
            self.state.printWorld()
            best_action = self.bestAction(percept)
            self.state.updateStateFromAction(best_action)
            return best_action

    def bestAction(self, percept):
        """
        Returns the best action regarding the current state of the game.
        """

        print("percept: ", percept)

        # finish game
        if self.state.isGoal():
            return CLIMB

        #  grab gold
        myself = self.state.getCell(self.state.posx, self.state.posy)
        if myself == GOLD:
            return GRAB

        #  Check neighbours
        directions_up = 0
        directions_right = 1
        directions_down = 2
        directions_left = 3

        possibilities = [
            directions_up,
            directions_right,
            directions_down,
            directions_left,
        ]

        for i, (x, y) in enumerate(
            self.state.getCellNeighbors(self.state.posx, self.state.posy)
        ):
            square = self.state.getCell(x, y)

            print(f"analise square {square} at position ({x}, {y})  i={i}")
            if square == VISITED or square == SAFE:
                continue

            elif square == WALL:
                possibilities.remove(i)

            elif square == WUMPUS:
                # TODO: check if its dead
                if i == self.state.direction and self.state.arrowInventory > 0:
                    return SHOOT
                else:
                    possibilities.remove(i)

            elif square == PIT:
                possibilities.remove(i)
                continue

            # coward approach
            elif square == WUMPUSP or square == PITP:
                possibilities.remove(i)
                continue

            elif square == UNKNOWN:
                if percept.stench and percept.breeze:
                    possibilities.remove(i)
                elif percept.stench and not percept.breeze:
                    if square == UNKNOWN or square == WUMPUSPITP:
                        if self.wumpusLocation == None:
                            possibilities.remove(i)

                    elif square == PITP:
                        continue
                elif not percept.stench and percept.breeze:
                    if square == UNKNOWN or square == WUMPUSPITP:
                        possibilities.remove(i)
                    elif square == WUMPUSP:
                        possibilities.remove(i)
        print(f"possibilities: {possibilities}")

        if len(possibilities) == 0:
            action = FORWARD
        else:
            n = len(possibilities)
            proba = [1] * n

            for i in range(n):
                x, y = self.state.getCellNeighbors(self.state.posx, self.state.posy)[
                    possibilities[i]
                ]
                if self.state.getCell(x, y) == SAFE:
                    proba[i] = 10
                elif (x - self.state.posx, y - self.state.posy) == DIRECTION_TABLE[
                    self.state.direction
                ]:
                    proba[i] = 5

            action = self.state.fromDirectionToAction(
                random.choices(possibilities, weights=proba)[0]
            )
            print(f"proba = {proba}")

        return action


#######
####### Exercise: Learning Agent
#######
class LearningAgent(Agent):
    """
    Your smartest Wumpus hunter brain.
    """

    isLearningAgent = True

    def init(self, gridSize):

        self.state = State(gridSize)
        " *** YOUR CODE HERE ***"

    def think(self, percept, action, score, isTraining):
        """
        Returns the best action regarding the current state of the game.
        Available actions are ['left', 'right', 'forward', 'shoot', 'grab', 'climb'].
        """
        " *** YOUR CODE HERE ***"


#######
####### Exercise: Environment
#######

WALL = "#"
UNKNOWN = "?"
WUMPUSP = "w"
WUMPUS = "W"
PITP = "p"
PIT = "P"
WUMPUSPITP = "x"
SAFE = " "
VISITED = "."
GOLD = "G"

RIGHT = "right"
LEFT = "left"
FORWARD = "forward"
CLIMB = "climb"
SHOOT = "shoot"
GRAB = "grab"

DIRECTION_TABLE = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # North, East, South, West


class State:
    def __init__(self, gridSize):
        self.size = gridSize
        self.worldmap = [
            [
                ((y in [0, gridSize - 1] or x in [0, gridSize - 1]) and WALL) or UNKNOWN
                for x in range(gridSize)
            ]
            for y in range(gridSize)
        ]
        self.direction = 1
        self.posx = 1
        self.posy = 1
        self.action = "left"
        self.setCell(self.posx, self.posy, self.agentAvatar())
        self.wumpusIsKilled = False
        self.goldIsGrabbed = False
        self.wumpusLocation = None
        self.arrowInventory = 1
        self.score = 0
        " *** YOUR CODE HERE ***"

    def printWorld(self):
        """
        For debugging purpose.
        """
        for y in range(self.size):
            for x in range(self.size):
                print(self.getCell(x, y) + " ", end=" ")
            print()

    def getCell(self, x, y):
        return self.worldmap[x][y]

    def setCell(self, x, y, value):
        self.worldmap[x][y] = value

    def getCellNeighbors(self, x, y):
        return [(x + dx, y + dy) for (dx, dy) in DIRECTION_TABLE]

    def getForwardPosition(self, x, y, direction):
        (dx, dy) = DIRECTION_TABLE[direction]
        return (x + dx, y + dy)

    def fromDirectionToAction(self, direction):
        if direction == self.direction:
            return FORWARD
        elif direction == (self.direction + 1) % 4:
            return RIGHT
        elif direction == (self.direction + 2) % 4:
            return RIGHT
        else:
            return LEFT

    def canGoForward(self):
        x1, y1 = self.getForwardPosition(self.posx, self.posy, self.direction)
        square = self.getCell(x1, y1)
        return square == VISITED

    def isGoal(self):
        return (
            (self.posx, self.posy) == (1, 1)
            # and self.arrowInventory == 0
            and self.goldIsGrabbed
        )

    def updateStateFromPercepts(self, percept, score):
        """
        Updates the current environment with regards to the percept information.
        """
        self.score = score
        #  Update neighbours
        self.setCell(self.posx, self.posy, VISITED)
        for x, y in self.getCellNeighbors(self.posx, self.posy):
            square = self.getCell(x, y)
            if square == WALL or square == VISITED or square == SAFE:
                continue
            if percept.stench and percept.breeze:
                if square == UNKNOWN and self.wumpusLocation == None:
                    self.setCell(x, y, WUMPUSPITP)
                else:
                    self.setCell(x, y, PITP)
            elif percept.stench and not percept.breeze:
                if square == UNKNOWN or square == WUMPUSPITP:
                    if self.wumpusLocation == None:
                        self.setCell(x, y, WUMPUSP)
                    else:
                        self.setCell(x, y, SAFE)
                elif square == PITP:
                    self.setCell(x, y, SAFE)
            elif not percept.stench and percept.breeze:
                if square == UNKNOWN or square == WUMPUSPITP:
                    self.setCell(x, y, PITP)
                elif square == WUMPUSP:
                    self.setCell(x, y, SAFE)
            else:
                self.setCell(x, y, SAFE)

        # Gold
        if percept.glitter:
            self.setCell(self.posx, self.posy, GOLD)

        # Kill Wumpus?
        if percept.scream:
            if self.wumpusLocation is not None:
                self.setCell(self.wumpusLocation[0], self.wumpusLocation[1], SAFE)
            self.wumpusIsKilled = True

        # Confirm Wumpus or Pit.
        for y in range(self.size):
            for x in range(self.size):
                if self.getCell(x, y) == VISITED:
                    wumpusCount = 0
                    for px, py in self.getCellNeighbors(x, y):
                        if self.getCell(px, py) in [WUMPUSP, WUMPUSPITP]:
                            wumpusCount += 1
                    if (
                        wumpusCount == 1
                    ):  # Confirmer WUMPI+USP et supprimer les autres WUMPUSP (il n'ya qu'un WUMPUS).
                        for px, py in self.getCellNeighbors(x, y):
                            if self.getCell(px, py) in [WUMPUSP, WUMPUSPITP]:
                                self.setCell(px, py, WUMPUS)
                                self.wumpusLocation = (px, py)
                                for y1 in range(self.size):
                                    for x1 in range(self.size):
                                        if self.getCell(x1, y1) == WUMPUSP:
                                            self.setCell(x1, y1, SAFE)
                                        if self.getCell(x1, y1) == WUMPUSPITP:
                                            self.setCell(x1, y1, PITP)
                                break
                    pitCount = 0
                    for px, py in self.getCellNeighbors(x, y):
                        if self.getCell(px, py) in [PIT, PITP, WUMPUSPITP]:
                            pitCount += 1
                    if pitCount == 1:
                        for px, py in self.getCellNeighbors(x, y):
                            if self.getCell(px, py) in [PIT, PITP, WUMPUSPITP]:
                                self.setCell(px, py, PIT)
                                break
        return self

    def updateStateFromAction(self, action):
        self.action = action
        if self.action == GRAB:
            self.goldIsGrabbed = True
            self.setCell(self.posx, self.posy, VISITED)
        elif self.action == LEFT:
            self.direction = (self.direction + 3) % 4
        elif self.action == RIGHT:
            self.direction = (self.direction + 1) % 4
        elif self.action == FORWARD:
            self.setCell(self.posx, self.posy, VISITED)
            self.posx, self.posy = self.getForwardPosition(
                self.posx, self.posy, self.direction
            )
        self.setCell(self.posx, self.posy, self.agentAvatar())

    def agentAvatar(self):
        if self.direction == 0:
            return "^"
        elif self.direction == 1:
            return ">"
        elif self.direction == 2:
            return "v"
        else:
            return "<"

    def getWumpusPlace(self):
        return self.wumpusLocation

    def isShootingPositionFor(self, x, y):
        if self.direction == 0 and self.posx == x and self.posy > y:
            return True
        if self.direction == 1 and self.posy == y and self.posx < x:
            return True
        if self.direction == 2 and self.posx == x and self.posy < y:
            return True
        if self.direction == 3 and self.posy == y and self.posx > x:
            return True
        return False
