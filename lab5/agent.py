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
# @author Raquel Maciel.
# @author Alexandre Arezes.
#

from __future__ import print_function
import pprint
import random
import copy
import sys
import time
import utils
from wumpusworld import Percept

DEBUG = False

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

# x left to right increasing
# y top to bottom increasing

class State:
    def __init__(self, gridSize: int):
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

    def printWorld(self) -> None:
        """
        For debugging purpose.
        """
        for y in range(self.size):
            for x in range(self.size):
                print(self.getCell(x, y) + " ", end=" ")
            print()

    def getCell(self, x: int, y: int) -> str:
        return self.worldmap[x][y]

    def setCell(self, x: int, y: int, value: str) -> None:
        self.worldmap[x][y] = value

    def getCellNeighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        return [(x + dx, y + dy) for (dx, dy) in DIRECTION_TABLE]

    def getNeighbors(self, x:int, y:int) -> list[str]:
        L = []
        for a, b in self.getCellNeighbors(x, y):
            if a >= 0 and a < self.size and b >= 0 and b < self.size:
                L.append(self.getCell(a, b))
        return L

    def getForwardPosition(self, x: int, y: int, direction: int) -> tuple[int, int]:
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
            and self.goldIsGrabbed
        )

    def updateStateFromPercepts(self, percept: Percept, score: float):
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

    def updateStateFromAction(self, action: str) -> None:
        self.action = action
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
            self.setCell(self.posx, self.posy, VISITED);
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

    def isShootingPositionFor(self, x:int, y:int) -> bool:
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
            self.state.updateStateFromPercepts(percept, score)
            self.state.printWorld()
            if DEBUG:
                reward = score - self.state.score
                print(f"reward : {reward}")
                print(f"pos : {self.state.getCell(self.state.posx, self.state.posy)}")
                print(f"gold : {self.state.goldIsGrabbed}")
                print(f"arrows : {self.state.arrowInventory}")
                print(f"x: {self.state.posx} y: {self.state.posy}")
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
        high = 10000
        medium = 100
        little = 1
        impossible = 0
        bonus = 10
        directions_description = ["up", "right", "down", "left"]
        directions_score = [impossible, impossible, impossible, impossible]

        for i, (x, y) in enumerate(
            self.state.getCellNeighbors(self.state.posx, self.state.posy)
        ):
            square = self.state.getCell(x, y)

            if DEBUG:
                print(
                    f"{i} - analising neighbor {square} at position ({x}, {y}) direction = {directions_description[i]}"
                )

            # the index matches the direction
            neighbor_direction = i
            is_same_direction = neighbor_direction == self.state.direction

            # switch case possible states
            if square == SAFE:
                directions_score[neighbor_direction] = high # to explore
                if DEBUG:
                    print(f"safe = {high}")

            elif square == VISITED:
                directions_score[neighbor_direction] = medium # to survive
                if DEBUG:
                    print(f"visited = {medium}")

            elif square == WALL:
                directions_score[neighbor_direction] = impossible
                if DEBUG:
                    print(f"wall = {impossible}")

            elif square == PIT:
                directions_score[neighbor_direction] = impossible
                if DEBUG:
                    print(f"pit = {impossible}")

            elif square == WUMPUS:
                if is_same_direction and self.state.arrowInventory > 0:
                    return SHOOT
                elif not is_same_direction and self.state.arrowInventory > 0:
                    directions_score[neighbor_direction] = high
                    if DEBUG:
                        print(f"close to wumpus = {high} (to turn at wumpus direction)")
                else:
                    directions_score[neighbor_direction] = impossible
                    if DEBUG:
                        print(f"no arrows = {impossible} (avoid wumpus)")

            elif square == WUMPUSP or square == PITP or square == WUMPUSPITP:
                directions_score[neighbor_direction] = little
                if DEBUG:
                    print(f"danger probability = {little}")

            # bonus
            if is_same_direction:
                directions_score[neighbor_direction] *= bonus # avoid unecessary turns
                if DEBUG:
                    print(f"same direction *{bonus}")

            if DEBUG:
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
            # get the path at the top of the queue
            current_path, cost = open_list.pop()
            if DEBUG:
                print(f"current path: {current_path}")
            # get the last place of that path
            current_position, current_direction = current_path[-1]
            if DEBUG:
                print(f"current position: {current_position}")
            # check if we have reached the goal
            if current_position == (1, 1):
                return current_path[1][1]
            else:
                # check were we can go from here
                # add the new paths (one step longer) to the queue
                for i, position in enumerate(
                    self.state.getCellNeighbors(
                        current_position[0], current_position[1]
                    )
                ):
                    # avoid loop!
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
    isTraining = False

    alpha = 0.1  # learning factor
    gamma = 0.9  # future vision factor
    epsilon = 0.1  # exploration factor

    state = None
    percept = None
    actions = ["left", "right", "forward", "shoot", "grab"]
    weights = utils.Counter()
    first = True

    def init(self, gridSize: int) -> None:
        # update weights after the last iteraction ends
        has_antecedent = self.state != None and self.percept != None
        if has_antecedent:
            self.state.updateStateFromPercepts(self.percept, self.state.score)
            reward = self.getReward(self.previous_state, self.state, isEnd=True)
            previous_weights = copy.deepcopy(self.weights)
            self.update(self.previous_state, self.previous_action, self.state, reward)
            if DEBUG:
                print(f"action : {self.previous_action}")
                print(f"reward : {reward}")
                print(f"previous weights : {previous_weights}")
                print(f"current weights : {self.weights}")

        self.previous_action = None
        self.state = State(gridSize)
        self.previous_state = self.state

        # removing climb as option at start to avoid tkinter bug
        self.actions = ["left", "right", "forward", "shoot", "grab"]
        self.first = True

    def think(
        self, percept: Percept, previous_action: str, score: float, isTraining: bool
    ) -> str:
        """
        Returns the best action regarding the current state of the game.
        Available actions are ['left', 'right', 'forward', 'shoot', 'grab', 'climb'].
        

        REINFORCEMENT LEARNING AGENT
        
        function INTELLIGENT-AGENT(percept, goal) returns an action
        static: state, the agent's memory of the world state
        state ← UPDATE-STATE-FROM-PERCEPTS(state, percept)
        IF previous_action != None
                LEARN_FROM_TRANSITION(previous_state, previous_action,
                                    state, reward)
        action ← CHOOSE-BEST-ACTION(state)
        state ← UPDATE-STATE-FROM-ACTION(state, action)
        previous_action ← action
        previous_state ← state
        return action
        
    """

        # taking off the learning wheels
        if not isTraining:
            self.alpha = 0.0
            self.epsilon = 0.0

        self.percept = percept

        ### REINFORCEMENT LEARNING AGENT
        self.state.updateStateFromPercepts(percept, score)

        if self.previous_action != None:
            reward = self.getReward(self.previous_state, self.state)
            if DEBUG:
                pprint.pprint(f"reward : {reward}")
                self.state.printWorld()
            self.update(self.previous_state, self.previous_action, self.state, reward)
        action = self.getBestAction(self.state)
        self.previous_state = copy.deepcopy(self.state)
        self.state.updateStateFromAction(action)
        self.previous_action = action

        if(self.first):
            self.actions.append(CLIMB)
            self.first = False

        return action

    def update(self, state: State, action: str, nextState: State, reward: int) -> None:
        """
        The parent class calls this method to observe a
        state = action => nextState and reward transition. 
        You should do your Q-Value update here

        NOTE: You should never call this method,
        it will be called on your behalf

        Abstraction using Approximated Linear Functions

        Q-Learning learning algorithm is used to learn the weight vector W, 
        similar to updating Q-values when a transition s → s’ by action a 
        occurs:
            ∀i, wi ← wi + α[difference] . fi(s, a)
            difference = [ R(s, a) + γ maxa’ Q(s', a')) ] - Q(s, a)
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

        if DEBUG:
            print(
                features,
                difference,
                reward,
                self.getQValue(state, action),
                self.computeActionFromQValues(nextState),
                self.weights,
            )


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

    def getBestAction(self, state: State) -> str:
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
        Abstraction using Approximated Linear Functions

        Q values becomes:
        Qf(s, a)= Σi wi . fi(s, a)
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

        next_state = copy.deepcopy(state)
        next_state.updateStateFromAction(action)
        next_x, next_y = next_state.posx, next_state.posy

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
        features["visited"] = state.getCell(next_x, next_y) == VISITED

        features["gold_is_grabbed"] = next_state.goldIsGrabbed
        if state.goldIsGrabbed:
            distance_to_start = next_state.getManhattanDistanceTo((1, 1))
            features["distance-to-start-after-catch-gold"] = distance_to_start
        # else:
        #     safe = state.getNearestCellEqualsTo(SAFE)
        #     if safe:
        #         features["distance-to-safe-before-catch-gold"] = (
        #             next_state.getManhattanDistanceTo(safe)
        #         )


        # features["kill-wumpus"] = (
        #     state.getWumpusPlace() != None
        #     and state.isShootingPositionFor(
        #         state.getWumpusPlace()[0], state.getWumpusPlace()[1]
        #     )
        #     and not state.wumpusIsKilled
        #     and state.arrowInventory > 0
        #     and action == SHOOT
        # )


        # Normalize features
        features.divideAll(10)

        return features


    def getReward(self, previous_state: State, current_state: State, isEnd=False) -> int:
        reward = current_state.score - previous_state.score
        if DEBUG:
            print(f"real reward { reward}")
        
        # NOTE state_A.action -> is the action who leads to the state_A

        if isEnd:
            if current_state.action == CLIMB and previous_state.isGoal():
                return 500 
            elif current_state.action == FORWARD: # killed because it walked to a pit/wumpus
                return -1000
            return 0

        if DEBUG:
            previous_state.printWorld()

        if current_state.action == SHOOT and not current_state.wumpusIsKilled:
            if DEBUG:
                print("useless shot")
            return -100
        elif current_state.action == SHOOT and previous_state.wumpusIsKilled:
            if DEBUG:
                print("useless shot")
            return -100
        elif (
            previous_state.getCell(current_state.posx, current_state.posy) == GOLD
            and current_state.action == GRAB
        ):
            if DEBUG:
                print("gold is grabbed")
            return 1000
        elif (
            not previous_state.wumpusIsKilled
            and current_state.action == SHOOT
            and current_state.wumpusIsKilled
            and WUMPUS
            in previous_state.getNeighbors(previous_state.posx, previous_state.posy)
        ):
            if DEBUG:
                print("wumpus is killed")
            return 100
        elif (previous_state.posx, previous_state.posy) == (
            current_state.posx,
            current_state.posy,
        ):
            if DEBUG:
                print("probably useless turn")
            return -50
        elif previous_state.getCell(current_state.posx, current_state.posy) == VISITED:
            if DEBUG:
                print("went to visited")
            return -1
        elif previous_state.getCell(current_state.posx, current_state.posy) == SAFE:
            if DEBUG:
                print("went to safe")
            return +5
        else:
            if DEBUG:
                print(f"went to other {previous_state.getCell(current_state.posx, current_state.posy)}")
            return -100
