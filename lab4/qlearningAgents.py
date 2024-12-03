# qlearningAgents.py
# ------------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and Pieter
# Abbeel in Spring 2013.
# For more info, see http://inst.eecs.berkeley.edu/~cs188/pacman/pacman.html

from game import *
from learningAgents import ReinforcementAgent
from featureExtractors import *
import random, util, math

#  ______                   _            __     ___
# |  ____|                 (_)          /_ |   |__ \
# | |__  __  _____ _ __ ___ _ ___  ___   | | _    ) |
# |  __| \ \/ / _ \ '__/ __| / __|/ _ \  | |(_)  / /
# | |____ >  <  __/ | | (__| \__ \  __/  | |    / /_
# |______/_/\_\___|_|  \___|_|___/\___|  |_|   |____|


class QLearningAgent(ReinforcementAgent):
    """
    Q-Learning Agent

    Functions you should fill in:
      - update
      - computeUtilityFromQValues
      - computeActionFromQValues

    Instance variables you have access to
      - self.epsilon (exploration rate <=1)
      - self.alpha (learning rate <=1)
      - self.discount (discount rate <=1)

    Functions you should use
      - self.getLegalActions(state) which returns legal actions for a state
    """

    def __init__(self, **args):
        """Initializes Q-values."""
        ReinforcementAgent.__init__(self, **args)
        self.QValues = util.Counter()

    def update(self, state, action, nextState, reward):
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

    def computeUtilityFromQValues(self, state):
        """
        Returns max_action Q(state,action)
        where the max is over all legal actions. Note that if
        there are no legal actions, which is the case at the
        terminal state, you should return a value of 0.0.
        """

        if len(self.getLegalActions(state)) == 0:
            return 0.0

        return max(
            [self.getQValue(state, action) for action in self.getLegalActions(state)]
        )

    def computeActionFromQValues(self, state):
        """
        Returns the best action to take in a state. Note that if there
        are no legal actions, which is the case at the terminal state,
        you should return None.
        """

        if len(self.getLegalActions(state)) == 0:
            return None

        qvalues = [
            self.getQValue(state, action) for action in self.getLegalActions(state)
        ]
        maxQ = self.computeUtilityFromQValues(state)
        w = [1 if Q == maxQ else 0 for Q in qvalues]
        return random.choices(self.getLegalActions(state), weights=w, k=1)[0]

    def getAction(self, state):
        """
        Compute the action to take in the current state.  With
        probability self.epsilon, we should take a random action and
        take the best policy action otherwise.  Note that if there are
        no legal actions, which is the case at the terminal state, you
        should choose None as the action.

        HINT: You might want to use util.flipCoin(prob)
        """
        "*** YOUR CODE INSTEAD OF THE FOLLOWING ***"
        if len(self.getLegalActions(state)) == 0:
            return None

        if util.flipCoin(self.epsilon):
            qvalues = [
                self.getQValue(state, action) for action in self.getLegalActions(state)
            ]
            maxQ = self.computeUtilityFromQValues(state)
            w = [0.0001 if Q == maxQ else 1 for Q in qvalues]
            return random.choices(self.getLegalActions(state), weights=w, k=1)[0]
        else:
            return self.computeActionFromQValues(state)

    def getQValue(self, state, action):
        """
        Returns Q(state, action)
        Should return 0.0 if we never seen
        a state or the (state, action) tuple
        """
        return self.QValues[state, action]

    def setQValue(self, state, action, value):
        """
        change Q(state, action)
        """
        self.QValues[state, action] = value

    def getPolicy(self, state):
        """
        Compute the best action to take in a state.  Note that if there
        are no legal actions, which is the case at the terminal state,
        you should return None.
        """
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        """
        Returns max_action Q(state,action)
        where the max is over legal actions.  Note that if
        there are no legal actions, which is the case at the
        terminal state, you should return a value of 0.0.
        """
        return self.computeUtilityFromQValues(state)


class PacmanQAgent(QLearningAgent):
    "Exactly the same as QLearningAgent, but with different default parameters"

    def __init__(self, epsilon=0.05, gamma=0.8, alpha=0.2, numTraining=0, **args):
        """
        These default parameters can be changed from the pacman.py command line.
        For example, to change the exploration rate, try:
            python pacman.py -p PacmanQLearningAgent -a epsilon=0.1

        alpha    - learning rate
        epsilon  - exploration rate
        gamma    - discount factor
        numTraining - number of training episodes, i.e. no learning after these many episodes
        """
        args["epsilon"] = epsilon
        args["gamma"] = gamma
        args["alpha"] = alpha
        args["numTraining"] = numTraining
        self.index = 0  # This is always Pacman
        QLearningAgent.__init__(self, **args)

    def getAction(self, state):
        """
        Simply calls the getAction method of QLearningAgent and then
        informs parent of action for Pacman.  Do not change or remove this
        method.
        """
        action = QLearningAgent.getAction(self, state)
        self.doAction(state, action)
        return action


#  ______                   _            ____
# |  ____|                 (_)          |___ \
# | |__  __  _____ _ __ ___ _ ___  ___    __) |
# |  __| \ \/ / _ \ '__/ __| / __|/ _ \  |__ <
# | |____ >  <  __/ | | (__| \__ \  __/  ___) |
# |______/_/\_\___|_|  \___|_|___/\___| |____/


class ApproximateQAgent(PacmanQAgent):
    """
    ApproximateQLearningAgent

    You should only have to overwrite getQValue
    and update.  All other QLearningAgent functions
    should work as is.
    """

    def __init__(self, extractor="IdentityExtractor", **args):
        self.featExtractor = util.lookup(extractor, globals())()
        PacmanQAgent.__init__(self, **args)
        self.weights = util.Counter()

    def getQValue(self, state, action):
        """
        Should return Q(state, action) = w * featureVector(state, action)
        where * is the dot product operator.

        Q(a, s) = Σiϵ{1,n} fi(s, a) wi
        """

        features = self.featExtractor.getFeatures(state, action)
        result = 0.0
        for f in features:
            result += self.weights[f] * features[f]

        return result

    def update(self, state, action, nextState, reward):
        """
        Should update your weights based on transition.

        wi ← wi + α[difference]fi(s,a)

        difference = (R(s,a) + γ maxa' Q(s',a'))-Q(s,a)
        """
        features = self.featExtractor.getFeatures(state, action)
        difference = (reward + self.gamma * max([self.getQValue(nextState, action) for action in self.getLegalActions(state)])) - self.getQValue(state, action)
        for f in features:
            self.weights[f] += self.alpha * difference * features[f]

    def final(self, state):
        """
        Called at the end of each game.
        """
        PacmanQAgent.final(self, state)

        # did we finish training?
        if self.episodesSoFar == self.numTraining:
            # you might want to print your weights here for debugging
            # print self.getWeights()
            pass

    def getWeights(self):
        return self.weights
