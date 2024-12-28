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

        self.state.updateStateFromPercepts(percept, score)
        self.state.printWorld()
        best_action = self.bestAction()
        self.state.updateStateFromAction(best_action)
        return best_action

    def bestAction(self):
        """
        Returns the best action regarding the current state of the game.
        """

        #  finish game
        if self.state.isGoal():
            return CLIMB

        #  go to start to finish the game
        if self.state.goldIsGrabbed:
            return self.state.fromDirectionToAction(
                self.AStar((self.state.posx, self.state.posy))
            )

        #  grab gold
        myposition = self.state.getCell(self.state.posx, self.state.posy)
        if myposition == GOLD:
            return GRAB

        #  check neighbours
        bonus = 5
        high = 100
        medium = 10
        little = 1
        impossible = 0
        directions_description = ["up", "right", "down", "left"]
        directions_score = [impossible, impossible, impossible, impossible]

        for i, (x, y) in enumerate(
            self.state.getCellNeighbors(self.state.posx, self.state.posy)
        ):
            square = self.state.getCell(x, y)

            print(
                f"{i} - analising neighbor {square} at position ({x}, {y}) direction = {directions_description[i]}"
            )

            # the index matches the direction
            neighbor_direction = i
            is_same_direction = neighbor_direction == self.state.direction

            # switch case possible states
            if square == SAFE:
                directions_score[neighbor_direction] = high
                print(f"safe = {high}")

            elif square == VISITED:
                directions_score[neighbor_direction] = medium
                print(f"visited = {medium}")

            elif square == WALL:
                directions_score[neighbor_direction] = impossible
                print(f"wall = {impossible}")

            elif square == PIT:
                directions_score[neighbor_direction] = impossible
                print(f"pit = {impossible}")

            elif square == WUMPUS:
                if is_same_direction and self.state.arrowInventory > 0:
                    return SHOOT
                elif self.state.arrowInventory > 0:
                    # impossible to go foward and kill himself because its not at the same direction
                    directions_score[neighbor_direction] = high
                    print(f"close to wumpus = {high}")
                else:
                    directions_score[neighbor_direction] = impossible
                    print(f"no arrows = {impossible}")

            # TODO: if its 2 walls and 2 pits its all 0 than bugs the random choices
            elif square == WUMPUSP or square == PITP or square == WUMPUSPITP:
                directions_score[neighbor_direction] = little
                print(f"danger probability = {little}")

            # bonus
            if is_same_direction:
                directions_score[neighbor_direction] *= bonus
                print(f"same direction *{bonus}")

            print(f"{directions_description[i]} = {directions_score[i]}")

        action = self.state.fromDirectionToAction(
            random.choices([0, 1, 2, 3], weights=directions_score)[0]
        )

        return action

    def heuristic(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        return abs(x1 - x2) + abs(y1 - y2)

    def AStar(self, initial_state):
        from utils import PriorityQueue

        open_list = PriorityQueue()
        open_list.push(
            [(initial_state, None)], self.heuristic(initial_state, (1, 1))
        )  # a state is a pair (board, direction)
        closed_list = set([initial_state])  # keep already explored positions

        while not open_list.isEmpty():
            # Get the path at the top of the queue
            current_path, cost = open_list.pop()
            print(current_path)
            # Get the last place of that path
            current_state, current_direction = current_path[-1]
            print(current_state)
            # Check if we have reached the goal
            if current_state == (1, 1):
                return current_path[1][1]
            else:
                # Check were we can go from here
                # Add the new paths (one step longer) to the queue
                for i, state in enumerate(
                    self.state.getCellNeighbors(current_state[0], current_state[1])
                ):
                    # Avoid loop!
                    if state not in closed_list:
                        square = self.state.getCell(state[0], state[1])
                        if square not in [WALL, WUMPUS, WUMPUSP, WUMPUSPITP, PIT, PITP]:
                            closed_list.add(state)
                            open_list.push(
                                current_path + [(state, i)],
                                (cost + 1 + self.heuristic(state, (1, 1))),
                            )
        return []


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

# x - -> +

# y
# -
# |
# v
# +

#   (-1,-1) (1,-1)
#   (-1, 1) (1, 1)


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
            # TODO: check if its mandatory
            # and self.arrowInventory == 0
            and self.goldIsGrabbed
        )

    def updateStateFromPercepts(self, percept, score):
        """
        Updates the current environment with regards to the percept information.
        """
        self.score = score

        # Update neighbours
        self.setCell(self.posx, self.posy, VISITED)

        # Update location of Pits and Wumpus
        for x, y in self.getCellNeighbors(self.posx, self.posy):
            square = self.getCell(x, y)
            if (
                square == WALL
                or square == VISITED
                or square == SAFE
                or square == WUMPUS
                or square == PIT
            ):
                continue
            if percept.stench and percept.breeze:
                if square == UNKNOWN:
                    if self.wumpusLocation == None:
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

        # Wumpus killed
        if percept.scream:
            self.wumpusIsKilled = True
            # Remove WUMPUS from all squares
            for x, y in self.getCellNeighbors(self.posx, self.posy):
                square = self.getCell(x, y)
                if square == WUMPUSP or square == WUMPUS:
                    self.setCell(x, y, SAFE)
                elif square == WUMPUSPITP:
                    self.setCell(x, y, PITP)

        # Confirm Wumpus or Pit
        for y in range(self.size):
            for x in range(self.size):
                if self.getCell(x, y) == VISITED:
                    # Count the number WUMPUSP in neighborhood
                    wumpusCount = 0
                    for px, py in self.getCellNeighbors(x, y):
                        if self.getCell(px, py) in [WUMPUSP, WUMPUSPITP]:
                            wumpusCount += 1
                    if (
                        wumpusCount == 1
                    ):  # Confirm WUMPUSP as WUMPUS and discard other WUMPUSP
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
                    # Count the number of PITP in neighborhood
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
