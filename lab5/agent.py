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
import pprint
import random
import copy
import sys
import utils
from wumpusworld import Percept


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

        # YOUR CODE HERE

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

    def getNeighbors(self, x, y):
        L = []
        for a, b in self.getCellNeighbors(x, y):
            if a >= 0 and a < self.size and b >= 0 and b < self.size:
                L.append(self.getCell(a, b))
        return L

    def getForwardPosition(self, x, y, direction: int) -> tuple[int, int]:
        (dx, dy) = DIRECTION_TABLE[direction]
        return (x + dx, y + dy)

    def fromDirectionToAction(self, direction: int) -> str:
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
            # TODO! add in the rapport
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
        # TODO! add this to rapport any grab would think that it had gold
        if self.action == GRAB and self.getCell(self.posx, self.posy) == GOLD:
            self.goldIsGrabbed = True
            self.setCell(self.posx, self.posy, VISITED)
        elif self.action == SHOOT:
            self.arrowInventory = 0
        elif self.action == LEFT:
            self.direction = (self.direction + 3) % 4
        elif self.action == RIGHT:
            self.direction = (self.direction + 1) % 4
        elif self.action == FORWARD:
            self.setCell(self.posx, self.posy, VISITED)

            # TODO! add this to the rapport to bump on the wall
            # self.posx, self.posy = self.getForwardPosition(
            #     self.posx, self.posy, self.direction
            # )
            x, y = self.getForwardPosition(self.posx, self.posy, self.direction)

            square = self.getCell(x, y)

            if square != WALL:
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

    def getWumpusPlace(self) -> tuple[int, int] | None:
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

    def getCellsIn(self, what: list[str]) -> list[tuple[int, int]]:
        result = []
        for x in range(self.size):
            for y in range(self.size):
                if self.getCell(x, y) in what:
                    result.append((x, y))
        return result

    def getCellsEqualTo(self, what: str) -> list[tuple[int, int]]:
        return self.getCellsIn([what])

    def getManhattanDistanceTo(self, pos: tuple[int, int]) -> int:
        return abs(self.posx - pos[0]) + abs(self.posy - pos[1])

    def getNearestCellEqualsTo(self, what: str) -> tuple[int, int]:
        min_dist = float("inf")
        min = None
        for x, y in self.getCellsEqualTo(what):
            dist = self.getManhattanDistanceTo((x, y))
            if dist < min_dist:
                min_dist = dist
                min = (x, y)
        return min


class Agent:
    """
    The base class for various flavors of the agent.
    This an implementation of the Strategy design pattern.
    """

    isLearningAgent = False

    def init(self, gridSize: int) -> None:
        raise Exception("Invalid Agent class, init() not implemented")

    def think(
        self, percept: Percept, action: str, score: float, isTraining: bool = False
    ):
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

    def init(self, gridSize: int) -> None:
        pass

    def think(
        self, percept: Percept, action: str, score: float, isTraining: bool = False
    ) -> str:
        return random.choice(["shoot", "grab", "left", "right", "forward", "forward"])


class HumanAgent(Agent):
    """
    Game version using keyboard to control the agent
    """

    def init(self, gridSize: int) -> None:
        self.state = State(gridSize)
        self.isStarted = False

    def think(
        self, percept: Percept, action: str, score: float, isTraining: bool = False
    ) -> str:
        """
        Returns the best action regarding the current state of the game.
        Available actions are ['left', 'right', 'forward', 'shoot', 'grab', 'climb'].
        """
        if not self.isStarted:
            self.isStarted = True
            return GRAB
        else:
            reward = score - self.state.score
            print(reward)
            self.state.updateStateFromPercepts(percept, score)
            print("pos : " + self.state.getCell(self.state.posx, self.state.posy))
            self.state.printWorld()
            print(f"gold : {self.state.goldIsGrabbed}")
            print(self.state.arrowInventory)
            print(f"x= {self.state.posx} y= {self.state.posy}")
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

    def init(self, gridSize: int) -> None:
        self.state = State(gridSize)
        " *** YOUR CODE HERE ***"

    def think(self, percept: Percept, action: str, score: float) -> str:
        """
        Returns the best action regarding the current state of the game.
        Available actions are ['left', 'right', 'forward', 'shoot', 'grab', 'climb'].


        state <- updateStateFromPercepts(percept)
        action <- bestAction(state)
        state <- updateStateFromAction(action)
        return action
        """

        self.state.updateStateFromPercepts(percept, score)
        self.state.printWorld()
        best_action = self.bestAction()
        self.state.updateStateFromAction(best_action)
        return best_action

    def bestAction(self) -> str:
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
        bonus = 2
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

            elif square == WUMPUSP or square == PITP or square == WUMPUSPITP:
                directions_score[neighbor_direction] = little
                print(f"danger probability = {little}")

            # bonus
            if is_same_direction:
                directions_score[neighbor_direction] *= bonus
                print(f"same direction *{bonus}")

            print(f"{directions_description[i]} = {directions_score[i]}")

        if sum(directions_score) == 0:
            directions_score = [1] * 4

        action = self.state.fromDirectionToAction(
            random.choices([0, 1, 2, 3], weights=directions_score)[0]
        )

        return action

    def heuristic(self, p1: tuple[int, int], p2: tuple[int, int]) -> int:
        x1, y1 = p1
        x2, y2 = p2
        return abs(x1 - x2) + abs(y1 - y2)

    def AStar(self, initial_position: tuple[int, int]) -> str:
        from utils import PriorityQueue

        open_list = PriorityQueue()
        open_list.push(
            [(initial_position, None)], self.heuristic(initial_position, (1, 1))
        )  # a state is a pair (board, direction)
        closed_list = set([initial_position])  # keep already explored positions

        while not open_list.isEmpty():
            # Get the path at the top of the queue
            current_path, cost = open_list.pop()
            print(current_path)
            # Get the last place of that path
            current_position, current_direction = current_path[-1]
            print(current_position)
            # Check if we have reached the goal
            if current_position == (1, 1):
                return current_path[1][1]
            else:
                # Check were we can go from here
                # Add the new paths (one step longer) to the queue
                for i, position in enumerate(
                    self.state.getCellNeighbors(
                        current_position[0], current_position[1]
                    )
                ):
                    # Avoid loop!
                    if position not in closed_list:
                        square = self.state.getCell(position[0], position[1])
                        if square not in [WALL, WUMPUS, WUMPUSP, WUMPUSPITP, PIT, PITP]:
                            closed_list.add(position)
                            if (
                                position[0] - current_position[0],
                                position[1] - current_position[1],
                            ) == DIRECTION_TABLE[i]:
                                w = 1
                            else:
                                w = 10
                            open_list.push(
                                current_path + [(position, i)],
                                (cost + w + self.heuristic(position, (1, 1))),
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

    alpha = 0.1
    gamma = 0.8
    epsilon = 0.05
    actions = ["left", "right", "forward", "shoot", "grab", "climb"]

    def init(self, gridSize: int) -> None:
        self.state = State(gridSize)
        self.QValues = utils.Counter()

    def think(
        self, percept: Percept, action: str, score: float, isTraining: bool
    ) -> str:
        """
        Returns the best action regarding the current state of the game.
        Available actions are ['left', 'right', 'forward', 'shoot', 'grab', 'climb'].
        """
        reward = score - self.state.score
        if isTraining:
            self.update(previous_state, action, next_state, reward)
            self.state.updateStateFromPercepts(percept, score)
            previous_state = copy.deepcopy(self.state)
            action = random.choice(self.actions)
            self.state.updateStateFromAction(action)
            next_state = copy.deepcopy(self.state)

        else:
            self.state.updateStateFromPercepts(percept, score)
            action = self.getAction(self.state)
            self.state.updateStateFromAction(action)
        return action

    def update(self, state: State, action: str, nextState, reward: int) -> None:
        """
        The parent class calls this method to observe a
        state = action => nextState and reward transition.
        You should do your Q-Value update here

        NOTE: You should never call this method,
        it will be called on your behalf

        Q k+1(s,a) ← (1-α) Qk(s,a) + α ( R(s) + γ maxa’ Qk(s’,a’) )
        """
        newValue = (1 - self.alpha) * self.getQValue(state, action) + self.alpha * (
            reward + self.gamma * self.computeUtilityFromQValues(nextState)
        )
        self.setQValue(state, action, newValue)

    def computeUtilityFromQValues(self, state: State) -> float:
        """
        Returns max_action Q(state,action)
        where the max is over all legal actions. Note that if
        there are no legal actions, which is the case at the
        terminal state, you should return a value of 0.0.
        """
        if len(self.actions) == 0:
            return 0.0

        return max([self.getQValue(state, action) for action in self.actions])

    def computeActionFromQValues(self, state: State) -> str:
        """
        Returns the best action to take in a state. Note that if there
        are no legal actions, which is the case at the terminal state,
        you should return None.
        """

        if len(self.actions) == 0:
            return None

        qvalues = [self.getQValue(state, action) for action in self.actions]
        maxQ = max(qvalues)
        w = [1 if Q == maxQ else 0 for Q in qvalues]
        return random.choices(self.actions, weights=w, k=1)[0]

    def getAction(self, state: State) -> str:
        """
        Compute the action to take in the current state.  With
        probability self.epsilon, we should take a random action and
        take the best policy action otherwise.  Note that if there are
        no legal actions, which is the case at the terminal state, you
        should choose None as the action.

        HINT: You might want to use util.flipCoin(prob)
        """

        if len(self.actions) == 0:
            return None

        if utils.flipCoin(self.epsilon):
            qvalues = [self.getQValue(state, action) for action in self.actions]
            maxQ = self.computeUtilityFromQValues(state)
            w = [0.0001 if Q == maxQ else 1 for Q in qvalues]
            return random.choices(self.actions, weights=w, k=1)[0]
        else:
            return self.computeActionFromQValues(state)

    def getQValue(self, state: State, action: str) -> float:
        """
        Returns Q(state, action)
        Should return 0.0 if we never seen
        a state or the (state, action) tuple
        """
        # TODO! define exactly what differs a state from another
        # TODO! add this difficulty to define the graph states q learning at the rapport
        return self.QValues[state, action]

    def setQValue(self, state: State, action: str, value: float) -> None:
        """
        change Q(state, action)
        """
        self.QValues[state, action] = value

    def getPolicy(self, state: State) -> str:
        """
        Compute the best action to take in a state.  Note that if there
        are no legal actions, which is the case at the terminal state,
        you should return None.
        """
        return self.computeActionFromQValues(state)

    def getValue(self, state: State) -> float:
        """
        Returns max_action Q(state,action)
        where the max is over legal actions.  Note that if
        there are no legal actions, which is the case at the
        terminal state, you should return a value of 0.0.
        """
        return self.computeUtilityFromQValues(state)


class Learning2Agent(LearningAgent):
    """
    Your smartest Wumpus hunter brain.
    """

    isLearningAgent = True
    alpha = 0.01
    gamma = 0.8
    epsilon = 0.05
    actions = ["left", "right", "forward", "shoot", "grab", "climb"]
    weights = utils.Counter()
    first = True

    def init(self, gridSize: int) -> None:
        self.state = State(gridSize)
        self.actions = ["left", "right", "forward", "shoot", "grab"]
        self.first = True

    def think(
        self, percept: Percept, action: str, score: float, isTraining: bool
    ) -> str:
        reward = score - self.state.score
        # print(f"reward : {reward}")
        self.state.updateStateFromPercepts(percept, score)
        if isTraining:
            print(f"action : {action}")
            print(f"reward : {reward}")
            print(f"score : {score}")
            previous_state = copy.deepcopy(self.state)
            best_action = random.choice(self.actions)
            self.state.updateStateFromAction(best_action)
            next_state = copy.deepcopy(self.state)
            self.update(previous_state, best_action, next_state, reward)

        else:
            best_action = self.getAction(self.state)
            self.state.updateStateFromAction(best_action)
        if best_action == SHOOT:
            self.state.arrowInventory = 0
        if self.first:
            self.actions.append("climb")
            self.first = False

        return best_action

    def update(self, state, action, nextState, reward):
        """
        The parent class calls this method to observe a
        state = action => nextState and reward transition.
        You should do your Q-Value update here

        NOTE: You should never call this method,
        it will be called on your behalf

        Q k+1(s,a) ← (1-α) Qk(s,a) + α ( R(s) + γ maxa’ Qk(s’,a’) )
        """

        features = self.getFeatures(state, action)
        difference = (
            reward + self.gamma * self.computeUtilityFromQValues(nextState)
        ) - self.getQValue(state, action)

        for f in features:
            self.weights[f] += self.alpha * difference * features[f]

    def getQValue(self, state, action):
        """
        Returns Q(state, action)
        Should return 0.0 if we never seen
        a state or the (state, action) tuple
        """
        features = self.getFeatures(state, action)
        result = 0.0
        for f in features:
            result += self.weights[f] * features[f]

        return result

    def getFeatures(self, state, action):
        """
        features : isGoldTaken
                   distanceToTheStart
                   wumpusIsKilled
                   nbDangerousSquare1CaseAway
        """

        features = utils.Counter()
        features["bias"] = 1.0

        dx, dy = DIRECTION_TABLE[state.direction]
        next_x, next_y = state.posx + dx, state.posy + dy
        square = state.getCell(next_x, next_y)

        features["isGoldGrabbed"] = 10.0 if state.goldIsGrabbed else 0.0
        features["isWumpusKilled"] = 1.0 if state.wumpusIsKilled else 0.0
        features["isWall"] = 1.0 if square == WALL else 0.0
        features["isMortalSquare"] = int(square in [WUMPUS, PIT])
        features["isDangerousSquare"] = int(square in [WUMPUSP, PITP, WUMPUSPITP])
        features["isDangerousSquare"] = int(square in [SAFE, VISITED])
        # features["win"] = 10 * int(
        #     state.goldIsGrabbed and action == CLIMB and next_x == 1 and next_y == 1
        # )

        dist = abs(state.posx - 1) + abs(state.posy - 1)
        features["distanceToStart"] = dist / state.size

        # features["#-of-mortal-square-1-step-away"] = sum(
        #     square in [WUMPUS, PIT]
        #     for square in state.getNeighbors(next_x, next_y)
        # )
        # features["#-of-dangerous-square-1-step-away"] = sum(
        #     square in [WUMPUSP, PITP, WUMPUSPITP]
        #     for square in state.getNeighbors(next_x, next_y)
        # )

        # features["#-of-visited-square-1-step-away"] = sum(
        #     square == VISITED for square in state.getNeighbors(next_x, next_y)
        # )

        # features["#-of-safe-square-1-step-away"] = sum(
        #     square == SAFE for square in state.getNeighbors(next_x, next_y)
        # )

        # Normalize
        features.normalize()
        # pprint.pprint(features)
        return features

    def getWeights(self):
        return self.weights


class Learning3Agent(LearningAgent):
    """
    Your smartest Wumpus hunter brain.
    """

    isLearningAgent = True
    alpha = 0.1
    gamma = 0.9
    epsilon = 0.8
    weights = utils.Counter()
    first = True
    isTraining = False
    state = None
    actions = ["left", "right", "forward", "shoot", "grab", "climb"]
    percept = None

    def init(self, gridSize: int) -> None:
        if self.state and self.isTraining:
            previous_state = copy.deepcopy(self.state)
            self.state.updateStateFromAction(self.best_action)
            next_state = copy.deepcopy(self.state)
            if previous_state.isGoal():
                reward = 500
            elif previous_state.getCell(next_state.posx, next_state.posy) in [
                WUMPUS,
                WUMPUSP,
                WUMPUSPITP,
                PIT,
                PITP,
            ]:
                reward = -1000
            else:
                reward = 0

            print(f"n re :  {reward}")

            self.update(previous_state, self.best_action, next_state, reward)

        self.state = State(gridSize)
        # TODO! add this to the rapport
        # removing climb to avoid bug
        self.actions = ["left", "right", "forward", "shoot", "grab"]
        self.first = True

    def think(
        self, percept: Percept, action: str, score: float, isTraining: bool
    ) -> str:
        print(f"action :  {action}")
        reward = score - self.state.score
        self.isTraining = isTraining
        self.percept = percept
        if isTraining:
            # self.state.printWorld()
            previous_state = copy.deepcopy(self.state)
            self.state.updateStateFromAction(action)
            self.state.updateStateFromPercepts(percept, score)
            next_state = copy.deepcopy(self.state)
            self.update(previous_state, action, next_state, reward)
            self.best_action = random.choice(self.actions)
        else:
            self.state.updateStateFromPercepts(percept, score)
            self.best_action = self.getAction(self.state)
            self.state.updateStateFromAction(self.best_action)

        if self.first:
            self.actions.append("climb")
            self.first = False

        return self.best_action

    def update(self, state, action, nextState, reward):
        """
        The parent class calls this method to observe a
        state = action => nextState and reward transition.
        You should do your Q-Value update here

        NOTE: You should never call this method,
        it will be called on your behalf

        Q k+1(s,a) ← (1-α) Qk(s,a) + α ( R(s) + γ maxa’ Qk(s’,a’) )
        """

        features = self.getFeatures(state, action)
        difference = (
            reward
            + self.gamma
            * max([self.getQValue(nextState, action) for action in self.actions])
        ) - self.getQValue(state, action)
        for f in features:
            self.weights[f] += self.alpha * difference * features[f]

    def getQValue(self, state, action):
        """
        Returns Q(state, action)
        Should return 0.0 if we never seen
        a state or the (state, action) tuple
        """
        features = self.getFeatures(state, action)
        result = 0.0
        for f in features:
            result += self.weights[f] * features[f]

        return result

    def getFeatures(self, state, action):
        """
        features : isGoldTaken
                   distanceToTheStart
                   wumpusIsKilled
                   nbDangerousSquare1CaseAway
        """

        features = utils.Counter()
        features["bias"] = 1.0
        next_state = copy.deepcopy(state)
        next_state.updateStateFromAction(action)
        next_state.updateStateFromPercepts(self.percept, state.score)

        next_x, next_y = next_state.posx, next_state.posy
        square = state.getCell(next_x, next_y)
        features["isGoldGrabbed"] = int(next_state.goldIsGrabbed)
        features["isWumpusKilled"] = 1.0 if next_state.wumpusIsKilled else 0.0
        features["isWall"] = 1.0 if self.percept.bump else 0.0
        features["isMortalSquare"] = int(square in [WUMPUS, PIT])
        features["isDangerousSquare"] = int(square in [WUMPUSP, PITP, WUMPUSPITP])
        features["isSafeSquare"] = int(square in [SAFE, VISITED])
        # features["isSameSquare"] = int((next_x, next_y) == (state.posx, state.posy))

        dist = abs(next_x - 1) + abs(next_y - 1)
        if next_state.goldIsGrabbed:
            features["distanceToStart"] = dist / state.size
        else:
            float("inf")
        # features["win"] = 10 * int(state.goldIsGrabbed) + 1 / (dist + 0.00001)

        features["#-of-mortal-square-1-step-away"] = sum(
            square in [WUMPUS, PIT]
            for square in next_state.getNeighbors(next_x, next_y)
        )
        features["#-of-dangerous-square-1-step-away"] = sum(
            square in [WUMPUSP, PITP, WUMPUSPITP]
            for square in next_state.getNeighbors(next_x, next_y)
        )

        features["#-of-visited-square-1-step-away"] = sum(
            square == VISITED for square in next_state.getNeighbors(next_x, next_y)
        )

        features["#-of-safe-square-1-step-away"] = sum(
            square == SAFE for square in next_state.getNeighbors(next_x, next_y)
        )

        # Normalize
        features.normalize()
        # pprint.pprint(features)
        return features

        # def getFeatures(self, state, action):
        #     """
        #     Extract features for the given state and action:
        #     - bias
        #     - isGoldGrabbed
        #     - isWumpusKilled
        #     - isWall
        #     - isMortalSquare
        #     - isDangerousSquare
        #     - isSafeSquare
        #     - distanceToStart
        #     - goldDistance
        #     - wumpusDistance
        #     - hasArrow
        #     - #-of-mortal-square-1-step-away
        #     - #-of-dangerous-square-1-step-away
        #     - #-of-visited-square-1-step-away
        #     - #-of-safe-square-1-step-away
        #     """
        #     features = utils.Counter()
        #     features["bias"] = 1.0

        #     next_state = copy.deepcopy(state)
        #     next_state.updateStateFromAction(action)

        #     next_x, next_y = next_state.posx, next_state.posy
        #     square = state.getCell(next_x, next_y)

        #     # Feature extraction
        #     features["isGoldGrabbed"] = 10.0 if next_state.goldIsGrabbed else 0.0
        #     features["isWumpusKilled"] = 1.0 if next_state.wumpusIsKilled else 0.0
        #     features["isWall"] = 1.0 if square == WALL else 0.0
        #     features["isMortalSquare"] = int(square in [WUMPUS, PIT])
        #     features["isDangerousSquare"] = int(square in [WUMPUSP, PITP, WUMPUSPITP])
        #     features["isSafeSquare"] = int(square in [SAFE])
        #     features["isVisitedSquare"] = int(square in [VISITED])

        #     if square == SAFE:
        #         features["isSafeSquare"] = 1.0
        #     elif square == VISITED:
        #         features["isSafeSquare"] = 0.1
        #     else:
        #         features["isSafeSquare"] = 0.0

        #     # Distance features
        #     dist_to_start = abs(next_x - 1) + abs(next_y - 1)
        #     features["distanceToStart"] = (
        #         dist_to_start / state.size if next_state.goldIsGrabbed else 0.0
        #     )

        #     # if state.goldPos:
        #     #     gold_dist = abs(next_x - state.goldPos[0]) + abs(next_y - state.goldPos[1])
        #     #     features["goldDistance"] = gold_dist / state.size

        #     # if state.wumpusPos and not state.wumpusIsKilled:
        #     #     wumpus_dist = abs(next_x - state.wumpusPos[0]) + abs(next_y - state.wumpusPos[1])
        #     #     features["wumpusDistance"] = wumpus_dist / state.size

        #     features["hasArrow"] = 1.0 if next_state.arrowInventory == 1 else 0.0

        #     # Nearby analysis
        #     neighbors = state.getNeighbors(next_x, next_y)
        #     features["#-of-mortal-square-1-step-away"] = sum(
        #         square in [WUMPUS, PIT] for square in neighbors
        #     )
        #     features["#-of-dangerous-square-1-step-away"] = sum(
        #         square in [WUMPUSP, PITP, WUMPUSPITP] for square in neighbors
        #     )
        #     features["#-of-visited-square-1-step-away"] = sum(
        #         square == VISITED for square in neighbors
        #     )
        #     features["#-of-safe-square-1-step-away"] = sum(
        #         square == SAFE for square in neighbors
        #     )

        # Normalize features
        features.normalize()

        return features

    def getWeights(self):
        return self.weights


# TODO! add to report
# Reinforcement learning is more difficult when the reward is far (eg. at
# the very end of a game).
class Learning4Agent(Agent):
    """
    Your smartest Wumpus hunter brain.
    """

    isLearningAgent = True
    alpha = 0.1  # learning factor
    gamma = 1  # future vision factor
    epsilon = 0.1  # exploration factor

    weights = utils.Counter()
    first = True
    isTraining = False
    state = None
    actions = ["left", "right", "forward", "shoot", "grab", "climb"]
    percept = None

    def init(self, gridSize: int) -> None:
        # TODO! add the need to learn the last move at the repport
        # Update values after
        if self.state and self.percept:
            self.state.updateStateFromPercepts(self.percept, self.state.score)

            reward = self.getReward(self.previous_state, self.state, isEnd=True)
            print(f"action : {self.previous_action}")

            print(f"reward : {reward}")

            self.update(self.previous_state, self.previous_action, self.state, reward)
            # print(f"n re :  {reward}")
            # print(f"LAST SCORE {self.state.score + reward}  \n")
            # print(f"self.weights after dead {self.weights}")

        self.previous_action = None
        self.state = State(gridSize)
        self.previous_state = self.state
        # TODO! add this to the rapport
        # removing climb to avoid bug
        self.actions = ["left", "right", "forward", "shoot", "grab"]
        self.first = True

    def think(
        self, percept: Percept, previous_action: str, score: float, isTraining: bool
    ) -> str:

        if not isTraining:
            self.alpha = 0.0
            self.epsilon = 0.0
        self.percept = percept
        self.state.updateStateFromPercepts(percept, score)

        # reward = self.state.score - self.previous_state.score
        reward = self.getReward(self.previous_state, self.state)
        if self.previous_action != None:
            self.update(self.previous_state, self.previous_action, self.state, reward)
        action = self.getAction(self.state)
        self.previous_state = copy.deepcopy(self.state)
        self.state.updateStateFromAction(action)
        self.previous_action = action

        if self.first:
            self.actions.append("climb")
            self.first = False

        return action

    def computeUtilityFromQValues(self, state: State) -> float:
        """
        Returns max_action Q(state,action)
        where the max is over all legal actions. Note that if
        there are no legal actions, which is the case at the
        terminal state, you should return a value of 0.0.
        """
        if len(self.actions) == 0:
            return 0.0

        return max([self.getQValue(state, action) for action in self.actions])

    def computeActionFromQValues(self, state: State) -> str:
        """
        Returns the best action to take in a state. Note that if there
        are no legal actions, which is the case at the terminal state,
        you should return None.
        """

        if len(self.actions) == 0:
            return None

        qvalues = [self.getQValue(state, action) for action in self.actions]
        maxQ = self.computeUtilityFromQValues(state)
        w = [1 if Q == maxQ else 0 for Q in qvalues]
        return random.choices(self.actions, weights=w, k=1)[0]

    def getAction(self, state: State) -> str:
        """
        Compute the action to take in the current state.  With
        probability self.epsilon, we should take a random action and
        take the best policy action otherwise.  Note that if there are
        no legal actions, which is the case at the terminal state, you
        should choose None as the action.

        HINT: You might want to use util.flipCoin(prob)
        """

        if len(self.actions) == 0:
            return None

        if utils.flipCoin(self.epsilon):
            qvalues = [self.getQValue(state, action) for action in self.actions]
            maxQ = self.computeUtilityFromQValues(state)
            w = [0.0001 if Q == maxQ else 1 for Q in qvalues]
            return random.choices(self.actions, weights=w, k=1)[0]
        else:
            return self.computeActionFromQValues(state)

    def update(self, state, action, nextState, reward, debug=False):
        """
        The parent class calls this method to observe a
        state = action => nextState and reward transition.
        You should do your Q-Value update here

        NOTE: You should never call this method,
        it will be called on your behalf

        Q k+1(s,a) ← (1-α) Qk(s,a) + α ( R(s) + γ maxa’ Qk(s’,a’) )
        """

        features = self.getFeatures(state, action)
        difference = (
            reward
            + self.gamma
            * max(
                [
                    self.getQValue(nextState, possible_next_action)
                    for possible_next_action in self.actions
                ]
            )
        ) - self.getQValue(state, action)
        for f in features:
            self.weights[f] += self.alpha * difference * features[f]

        if debug:
            print(
                features,
                difference,
                reward,
                self.getQValue(state, action),
                self.computeActionFromQValues(nextState),
                self.weights,
            )
        # self.weights.normalize()

    def getQValue(self, state, action):
        """
        Returns Q(state, action)
        Should return 0.0 if we never seen
        a state or the (state, action) tuple
        """
        features = self.getFeatures(state, action)
        result = 0.0
        for f in features:
            result += self.weights[f] * features[f]

        return result

    def getFeatures(self, state: State, action: str):
        """
        features : isGoldTaken
                   distanceToTheStart
                   wumpusIsKilled
                   nbDangerousSquare1CaseAway
        """

        features = utils.Counter()
        features["bias"] = 1.0

        okay_cells = state.getCellsEqualTo(VISITED)
        wall_cells = state.getCellsEqualTo(WALL)
        interesting_cells = state.getCellsEqualTo(SAFE)
        dangerous_cells = state.getCellsIn([PITP, WUMPUSP, WUMPUSPITP])
        mortal_cells = state.getCellsIn([PIT, WUMPUS])
        gold_position = state.getCellsEqualTo(GOLD)

        next_state = copy.deepcopy(state)
        next_state.updateStateFromAction(action)
        x, y = state.posx, state.posy
        next_x, next_y = next_state.posx, next_state.posy
        # if not next_state.goldIsGrabbed:
        # features["grab-gold"] =( (state.getCell(x, y) == GOLD) and action == GRAB)
        # features["grab-gold"] = not state.goldIsGrabbed and next_state.goldIsGrabbed
        # if features["grab-gold"] != 0:
        #     print("FINALMENTE PEGAR OUROOOOOOOOOOOOOOOOOO")
        # next_state.goldIsGrabbed = features["grab-gold"]

        # print(f"dangerous cells : {dangerous_cells}")
        # print(f"cell :{state.getCell(next_x, next_y)}")

        features["safe"] = state.getCell(next_x, next_y) == SAFE
        features["dangerous"] = state.getCell(next_x, next_y) in [
            WUMPUSP,
            WUMPUSPITP,
            PITP,
        ]
        features["mortal"] = state.getCell(next_x, next_y) in [WUMPUS, PIT]
        features["gold"] = state.getCell(next_x, next_y) == GOLD
        if state.goldIsGrabbed:
            distance_to_start = next_state.getManhattanDistanceTo((1, 1))
            features["distance-to-start-after-catch-gold"] = 1 / (
                distance_to_start + 0.0001
            )

        # if features["dangerous"] :
        #      print("oi")
        # features["safe"] = state.getCell(next_x, next_y) == SAFE

        # distance_to_start = next_state.getManhattanDistanceTo((1,1))

        # features["distance-to-start-before-catch-gold"] = (
        #     distance_to_start #if not next_state.goldIsGrabbed else 0
        # )
        # # features["distance-to-start-after-catch-gold"] = (
        # #     1 / (distance_to_start + 0.01) if next_state.goldIsGrabbed else 0
        # # )

        # features["dont go"] = state.getCell(next_x, next_y) in [
        #     PIT,
        #     WUMPUS,
        #     PITP,
        #     WUMPUSP,
        #     WUMPUSPITP,
        # ] and action == FORWARD

        # features["go"] = (1 - features["dont go"]) and action==FORWARD

        # if(len(gold_position) != 0):
        #     features["grab-gold"] = 1/(next_state.getManhattanDistanceTo(gold_position[0]) + 0.01)

        # features["shoot-wumpus"] = (
        #     state.getWumpusPlace() != None
        #     and state.isShootingPositionFor(
        #         state.getWumpusPlace()[0], state.getWumpusPlace()[1]
        #     )
        #     # and not state.wumpusIsKilled
        #     and state.arrowInventory > 0
        #     and action == SHOOT
        # )

        # Normalize features
        # features.divideAll(10)

        return features

    def getWeights(self):
        return self.weights

    def getReward(self, previous_state: State, new_state: State, isEnd=False) -> int:
        reward = new_state.score - previous_state.score
        if isEnd:
            if new_state.action == CLIMB and previous_state.goldIsGrabbed:
                return 500
            elif new_state.action == FORWARD:
                return -1000
            return 0

        # previous_state.printWorld()

        if previous_state.getCell(new_state.posx, new_state.posy) == VISITED:
            # print("Visited visited")
            return -1
        elif previous_state.getCell(new_state.posx, new_state.posy) == SAFE:
            # print("Visited safe")
            return +10
        elif (
            previous_state.getCell(new_state.posx, new_state.posy) == GOLD
            and new_state.action == GRAB
        ):
            print("gold is grabbed")
            return 1000
        else:
            # print(f"Visited other {previous_state.getCell(new_state.posx, new_state.posy)}")
            return -100


class Learning5Agent(Agent):
    """
    Your smartest Wumpus hunter brain.
    """

    isLearningAgent = True
    alpha = 0.1  # learning factor
    gamma = 0.9  # future vision factor
    epsilon = 0.1  # exploration factor

    weights = utils.Counter()
    first = True
    isTraining = False
    state = None
    actions = ["left", "right", "forward", "shoot", "grab", "climb"]
    percept = None

    def init(self, gridSize: int) -> None:
        # TODO! add the need to learn the last move at the repport
        # Update values after
        if self.state and self.percept:
            self.state.updateStateFromPercepts(self.percept, self.state.score)

            reward = self.getReward(self.previous_state, self.state, isEnd=True)
            print(f"action : {self.previous_action}")

            print(f"reward : {reward}")

            self.update(self.previous_state, self.previous_action, self.state, reward)
            # print(f"n re :  {reward}")
            # print(f"LAST SCORE {self.state.score + reward}  \n")
            # print(f"self.weights after dead {self.weights}")

        self.previous_action = None
        self.state = State(gridSize)
        self.previous_state = self.state
        # TODO! add this to the rapport
        # removing climb to avoid bug
        self.actions = ["left", "right", "forward", "shoot", "grab"]
        self.first = True

    def think(
        self, percept: Percept, previous_action: str, score: float, isTraining: bool
    ) -> str:

        if not isTraining:
            self.alpha = 0.0
            self.epsilon = 0.0
        self.percept = percept
        self.state.updateStateFromPercepts(percept, score)

        # reward = self.state.score - self.previous_state.score
        reward = self.getReward(self.previous_state, self.state)
        if self.previous_action != None:
            self.update(self.previous_state, self.previous_action, self.state, reward)
        action = self.getAction(self.state)
        self.previous_state = copy.deepcopy(self.state)
        self.state.updateStateFromAction(action)
        self.previous_action = action

        if self.first:
            self.actions.append("climb")
            self.first = False

        return action

    def computeUtilityFromQValues(self, state: State) -> float:
        """
        Returns max_action Q(state,action)
        where the max is over all legal actions. Note that if
        there are no legal actions, which is the case at the
        terminal state, you should return a value of 0.0.
        """
        if len(self.actions) == 0:
            return 0.0

        return max([self.getQValue(state, action) for action in self.actions])

    def computeActionFromQValues(self, state: State) -> str:
        """
        Returns the best action to take in a state. Note that if there
        are no legal actions, which is the case at the terminal state,
        you should return None.
        """

        if len(self.actions) == 0:
            return None

        qvalues = [self.getQValue(state, action) for action in self.actions]
        maxQ = self.computeUtilityFromQValues(state)
        w = [1 if Q == maxQ else 0 for Q in qvalues]
        return random.choices(self.actions, weights=w, k=1)[0]

    def getAction(self, state: State) -> str:
        """
        Compute the action to take in the current state.  With
        probability self.epsilon, we should take a random action and
        take the best policy action otherwise.  Note that if there are
        no legal actions, which is the case at the terminal state, you
        should choose None as the action.

        HINT: You might want to use util.flipCoin(prob)
        """

        if len(self.actions) == 0:
            return None

        if utils.flipCoin(self.epsilon):
            qvalues = [self.getQValue(state, action) for action in self.actions]
            maxQ = self.computeUtilityFromQValues(state)
            w = [0.0001 if Q == maxQ else 1 for Q in qvalues]
            return random.choices(self.actions, weights=w, k=1)[0]
        else:
            return self.computeActionFromQValues(state)

    def update(self, state, action, nextState, reward, debug=False):
        """
        The parent class calls this method to observe a
        state = action => nextState and reward transition.
        You should do your Q-Value update here

        NOTE: You should never call this method,
        it will be called on your behalf

        Q k+1(s,a) ← (1-α) Qk(s,a) + α ( R(s) + γ maxa’ Qk(s’,a’) )
        """

        features = self.getFeatures(state, action)
        difference = (
            reward
            + self.gamma
            * max(
                [
                    self.getQValue(nextState, possible_next_action)
                    for possible_next_action in self.actions
                ]
            )
        ) - self.getQValue(state, action)
        for f in features:
            self.weights[f] += self.alpha * difference * features[f]

        if debug:
            print(
                features,
                difference,
                reward,
                self.getQValue(state, action),
                self.computeActionFromQValues(nextState),
                self.weights,
            )
        # self.weights.normalize()

    def getQValue(self, state, action):
        """
        Returns Q(state, action)
        Should return 0.0 if we never seen
        a state or the (state, action) tuple
        """
        features = self.getFeatures(state, action)
        result = 0.0
        for f in features:
            result += self.weights[f] * features[f]

        return result

    def getFeatures(self, state: State, action: str):
        """
        features : isGoldTaken
                   distanceToTheStart
                   wumpusIsKilled
                   nbDangerousSquare1CaseAway
        """

        features = utils.Counter()
        features["bias"] = 1.0

        okay_cells = state.getCellsEqualTo(VISITED)
        wall_cells = state.getCellsEqualTo(WALL)
        interesting_cells = state.getCellsEqualTo(SAFE)
        dangerous_cells = state.getCellsIn([PITP, WUMPUSP, WUMPUSPITP])
        mortal_cells = state.getCellsIn([PIT, WUMPUS])
        gold_position = state.getCellsEqualTo(GOLD)

        next_state = copy.deepcopy(state)
        next_state.updateStateFromAction(action)
        x, y = state.posx, state.posy
        next_x, next_y = next_state.posx, next_state.posy
        # if not next_state.goldIsGrabbed:
        # features["grab-gold"] =( (state.getCell(x, y) == GOLD) and action == GRAB)
        # features["grab-gold"] = not state.goldIsGrabbed and next_state.goldIsGrabbed
        # if features["grab-gold"] != 0:
        #     print("FINALMENTE PEGAR OUROOOOOOOOOOOOOOOOOO")
        # next_state.goldIsGrabbed = features["grab-gold"]

        # print(f"dangerous cells : {dangerous_cells}")
        # print(f"cell :{state.getCell(next_x, next_y)}")
        # TODO: agent on wumpus : stuck
        features["climb_without_gold"] = (state.posx, state.posy) == (
            1,
            1,
        ) and not state.goldIsGrabbed
        features["same-square"] = (state.posx, state.posy) == (
            next_state.posx,
            next_state.posy,
        ) and not state.isGoal()
        features["safe"] = state.getCell(next_x, next_y) == SAFE
        features["dangerous"] = state.getCell(next_x, next_y) in [
            WUMPUSP,
            WUMPUSPITP,
            PITP,
        ]
        features["mortal"] = state.getCell(next_x, next_y) in [WUMPUS, PIT]
        features["gold"] = next_state.goldIsGrabbed
        if state.goldIsGrabbed:
            distance_to_start = next_state.getManhattanDistanceTo((1, 1))
            features["distance-to-start-after-catch-gold"] = distance_to_start
        # else:
        #     safe = state.getNearestCellEqualsTo(SAFE)
        #     if safe:
        #         features["distance-to-safe-before-catch-gold"] = (
        #             next_state.getManhattanDistanceTo(safe)
        #         )

        # features["wumpus-in-front"] = (
        #     state.wumpusLocation != None
        #     and next_state.isShootingPositionFor(
        #         state.getWumpusPlace()[0], state.getWumpusPlace()[1]
        #     )
        # )

        # features["arrow"] = state.arrowInventory
        # dx, dy = DIRECTION_TABLE[state.direction]
        # if features["arrow"]:
        #     features["wumpus"] = (
        #         not state.wumpusIsKilled
        #         and state.getCell(x+dx, y+dy) == WUMPUS
        #     )

        # if features["dangerous"] :
        #      print("oi")
        # features["safe"] = state.getCell(next_x, next_y) == SAFE

        # distance_to_start = next_state.getManhattanDistanceTo((1,1))

        # features["distance-to-start-before-catch-gold"] = (
        #     distance_to_start #if not next_state.goldIsGrabbed else 0
        # )
        # # features["distance-to-start-after-catch-gold"] = (
        # #     1 / (distance_to_start + 0.01) if next_state.goldIsGrabbed else 0
        # # )

        # features["dont go"] = state.getCell(next_x, next_y) in [
        #     PIT,
        #     WUMPUS,
        #     PITP,
        #     WUMPUSP,
        #     WUMPUSPITP,
        # ] and action == FORWARD

        # features["go"] = (1 - features["dont go"]) and action==FORWARD

        # if(len(gold_position) != 0):
        #     features["grab-gold"] = 1/(next_state.getManhattanDistanceTo(gold_position[0]) + 0.01)

        # Normalize features
        # features.divideAll(10)

        return features

    def getWeights(self):
        return self.weights

    def getReward(self, previous_state: State, new_state: State, isEnd=False) -> int:
        reward = new_state.score - previous_state.score
        if isEnd:
            if new_state.action == CLIMB and previous_state.goldIsGrabbed:
                return 500
            elif new_state.action == FORWARD:
                return -1000
            return 0

        # previous_state.printWorld()
        if new_state.action == SHOOT and not new_state.wumpusIsKilled:
            # print("inutile shot")
            return -100
        elif new_state.action == SHOOT and previous_state.wumpusIsKilled:
            # print("inutile shot")
            return -100
        elif (
            previous_state.getCell(new_state.posx, new_state.posy) == GOLD
            and new_state.action == GRAB
        ):
            print("gold is grabbed")
            return 1000
        elif (
            not previous_state.wumpusIsKilled
            and new_state.wumpusIsKilled
            and WUMPUS
            in previous_state.getNeighbors(previous_state.posx, previous_state.posy)
        ):
            print("wumpus is killed")
            return 100
        elif (previous_state.posx, previous_state.posy) == (
            new_state.posx,
            new_state.posy,
        ):
            return -50
        elif previous_state.getCell(new_state.posx, new_state.posy) == VISITED:
            # print("Visited visited")
            return -1
        elif previous_state.getCell(new_state.posx, new_state.posy) == SAFE:
            # print("Visited safe")
            return +5
        else:
            # print(f"Visited other {previous_state.getCell(new_state.posx, new_state.posy)}")
            return -100
