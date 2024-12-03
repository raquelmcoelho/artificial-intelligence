# valueIterationAgents.py
# -----------------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and Pieter 
# Abbeel in Spring 2013.
# For more info, see http://inst.eecs.berkeley.edu/~cs188/pacman/pacman.html

import sys
import mdp, util
import pdb

from learningAgents import ValueEstimationAgent

class ValueIterationAgent(ValueEstimationAgent):
    """
      A ValueIterationAgent takes a Markov decision process
      (see mdp.py) on initialization and runs value iteration
      for a given number of iterations using the supplied
      discount factor.
    """

    def __init__(self, mdp, gamma = 0.9, iterations = 100):
        """
        Your value iteration agent should take an mdp on
        construction, run the indicated number of iterations
        and then act according to the resulting policy.
        
        Some useful mdp methods you will use:
          mdp.getStates()
          mdp.getPossibleActions(state)
          mdp.getTransitionStatesAndProbs(state, action)
          mdp.getReward(state)
        """
        self.mdp = mdp
        self.gamma = gamma
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default values as 0
        "*** YOUR CODE HERE ***"
        # util.raiseNotDefined()
        self.runValueIteration(iterations)

    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state, self.iterations]

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)
    
    def runValueIteration(self, iterations):
        """
        Calcul de V(s) par iteration de la valeur
        en utilisant le nombre d'iterations.
        Version un peu lourde puisqu'elle utilise 'iterations' vecteurs de V(s).
        """
        self.count = 0
        while self.count < iterations:
            self.count += 1
            for state in self.mdp.getStates():
                possibleActions = self.mdp.getPossibleActions(state)
                if len(possibleActions) == 0:
                    continue
                # Calcul de Q(s,a)
                QValues = {}
                for action in possibleActions:
                    if action == "exit":
                        finalScore = self.mdp.getReward(state)
                        self.values[state, self.count] = finalScore
                        continue
                    else:
                        QValues[action] = self.getQValue(state, action)
                # Recherche du maximum puisque V(s) = max_a Q(s,a)
                maxAction = None
                maxQ = -1e30
                for key, value in QValues.items():
                    if value > maxQ:
                        maxAction = key
                        maxQ = value
                        if maxQ != -1e30 - 1:
                            self.values[state, self.count] = maxQ
    
    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        maxAction = None
        possibleActions = self.mdp.getPossibleActions(state)
        allQValues = []
        if len(possibleActions) == 0:
            return None
        for action in possibleActions:
            qValue = self.getQValue(state, action)
            if len(allQValues) == 0 or qValue > max(allQValues):
                maxAction = action
            allQValues.append(qValue)
        # TODO manque le random: facultatif
        return maxAction
    
    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        nextTransitions = self.mdp.getTransitionStatesAndProbs(state, action)
        qValue = 0
        reward = self.mdp.getReward(state)
        for transition in nextTransitions:
            previousValue = self.values[transition[0], self.count - 1]
            qValue += reward + self.gamma * (transition[1] * previousValue)
        return qValue
