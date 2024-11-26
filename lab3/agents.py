# -*- coding: utf-8 -*-
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
# @author John DeNero and Dan Klein - UC Berkeley
# @version Regis Clouard.
#

from __future__ import print_function
from game import Directions
import random, utils
import sys

from game import Agent

def scoreEvaluationFunction( currentGameState ):
  """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
  """
  return currentGameState.getScore()

def pause( text):
    if sys.version_info.major >= 3:
        input(text)
    else:
        raw_input(text)

######
###### Abstract class SearchAgent
######

class SearchAgent( Agent ):
  """
    This abstract class provides some common elements to all of your
    agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    YOU *DO NOT* NEED TO MAKE ANY CHANGES HERE.
  """

  def __init__( self, evalFn = 'scoreEvaluationFunction', depth = '2' ):
    self.index = 0 # Pacman is always agent index 0
    self.evaluationFunction = utils.lookup(evalFn, globals())
    self.depth = int(depth)
    
  def isTerminalNode( self, gameState, depth ):
    return gameState.isLose() or gameState.isWin() or depth == 0

######
###### MinimaxAgent1 : Minimax against 1 ghost
######
class MinimaxAgent1( SearchAgent ):
  """
  Minimax agent assuming that there exists only one ghost. 
  """

  def getAction( self, gameState ):
    """
    Returns the minimax action from the current gameState using self.depth
    and self.evaluationFunction.
    """  
    trueDepth = 2 * self.depth # Warning: use complete moves
    legalActions = gameState.getLegalActions(0)
    
    nextStatesFromLegalActions = [gameState.generateSuccessor(0, action) for action in legalActions]
    # Call recursive minimax
    values = [self.miniMaxValue(1, nextGameState, trueDepth - 1) for nextGameState in nextStatesFromLegalActions] 

    # Get the index of all tie max values
    listOfAllMaxValues = []
    maxValue = max(values)
    # print("max=", maxValue)
    # pause("next")

    for i in range(0, len(values)):
      if values[i] == maxValue:
        listOfAllMaxValues.append(i)
        
    # Random when there is a tie
    idx = random.randint(0, len(listOfAllMaxValues) - 1)
    action = legalActions[listOfAllMaxValues[idx]]
    return action

  def miniMaxValue(self, agentIndex, gameState, depth ):
    if self.isTerminalNode(gameState, depth):
      return self.evaluationFunction(gameState)    
    else:
      legalActions = gameState.getLegalActions(agentIndex)
      nextStatesFromLegalActions = [gameState.generateSuccessor(agentIndex, action) for action in legalActions]
      if agentIndex == 0: # if it's Pacman then it's a max layer
        return max([self.miniMaxValue(1 - agentIndex, nextState, depth - 1) for nextState in nextStatesFromLegalActions])
      else: # else if it's the ghost, then it's a min layer
        return min([self.miniMaxValue(1 - agentIndex, nextState, depth - 1) for nextState in nextStatesFromLegalActions])

#  ______                   _            __ 
# |  ____|                 (_)          /_ |
# | |__  __  _____ _ __ ___ _ ___  ___   | |
# |  __| \ \/ / _ \ '__/ __| / __|/ _ \  | |
# | |____ >  <  __/ | | (__| \__ \  __/  | |
# |______/_/\_\___|_|  \___|_|___/\___|  |_|

class MinimaxAgentN( SearchAgent ):
  """
  Minimax agent with n ghosts.
  """
  def getAction( self, gameState ):



    """
    Returns the minimax action from the current gameState using self.depth
    and self.evaluationFunction.
    """

    trueDepth = gameState.getNumberOfAgents() * self.depth # Warning: use complete moves
    legalActions = gameState.getLegalActions(0)
    
    nextStatesFromLegalActions = [gameState.generateSuccessor(0, action) for action in legalActions]
    # Call recursive minimax
    values = [self.miniMaxValue(0, nextGameState, trueDepth - 1) for nextGameState in nextStatesFromLegalActions] 

    # Get the index of all tie max values
    listOfAllMaxValues = []
    maxValue = max(values)
    # print("max=", maxValue)
    # pause("next")

    for i in range(0, len(values)):
      if values[i] == maxValue:
        listOfAllMaxValues.append(i)
        
    # Random when there is a tie
    idx = random.randint(0, len(listOfAllMaxValues) - 1)
    action = legalActions[listOfAllMaxValues[idx]]
    return action

  def miniMaxValue( self, agentIndex, gameState, depth ):
    if self.isTerminalNode(gameState, depth):
      return self.evaluationFunction(gameState)    
    else:
      legalActions = gameState.getLegalActions(agentIndex)
      nextStatesFromLegalActions = [gameState.generateSuccessor(agentIndex, action) for action in legalActions]
      if agentIndex == 0: # if it's Pacman then it's a max layer
        return max([self.miniMaxValue(1, nextState, depth - 1) for nextState in nextStatesFromLegalActions])
      else: # else if it's a ghost, then it's a min layer
        index = (agentIndex + 1) % gameState.getNumberOfAgents()
        return min([self.miniMaxValue(index, nextState, depth - 1) for nextState in nextStatesFromLegalActions])




#  ______                   _            ___  
# |  ____|                 (_)          |__ \ 
# | |__  __  _____ _ __ ___ _ ___  ___     ) |
# |  __| \ \/ / _ \ '__/ __| / __|/ _ \   / / 
# | |____ >  <  __/ | | (__| \__ \  __/  / /_ 
# |______/_/\_\___|_|  \___|_|___/\___| |____|

class AlphaBetaAgent(SearchAgent):
  """ 
  Your minimax agent with alpha-beta pruning.
  """
  
  def getAction(self, gameState):
    """
      Returns the minimax action using self.depth and self.evaluationFunction
    """
    trueDepth = gameState.getNumberOfAgents() * self.depth # Warning: use complete moves
    legalActions = gameState.getLegalActions(0)
    
    nextStatesFromLegalActions = [gameState.generateSuccessor(0, action) for action in legalActions]
    # Call recursive minimax
    values = [self.miniMaxValue(0, nextGameState, trueDepth - 1, -float('inf'), float('inf')) for nextGameState in nextStatesFromLegalActions] 

    # Get the index of all tie max values
    listOfAllMaxValues = []
    maxValue = max(values)
    # print("max=", maxValue)
    # pause("next")

    for i in range(0, len(values)):
      if values[i] == maxValue:
        listOfAllMaxValues.append(i)
        
    # Random when there is a tie
    idx = random.randint(0, len(listOfAllMaxValues) - 1)
    action = legalActions[listOfAllMaxValues[idx]]
    return action

  def miniMaxValue( self, agentIndex, gameState, depth , alpha, beta ):
    if self.isTerminalNode(gameState, depth):
      return self.evaluationFunction(gameState)    
    else:
      
      legalActions = gameState.getLegalActions(agentIndex)
      nextStatesFromLegalActions = [gameState.generateSuccessor(agentIndex, action) for action in legalActions]
      if agentIndex == 0: # if it's Pacman then it's a max layer
        v = -float('inf')
        for nextState in nextStatesFromLegalActions:
          v = max(v, self.miniMaxValue(1, nextState, depth - 1, alpha, beta))
          if v >= beta :
            return v
          alpha = max(alpha, v)
        return v
      else: # else if it's a ghost, then it's a min layer
        index = (agentIndex + 1) % gameState.getNumberOfAgents()
        v = float('inf')
        for nextState in nextStatesFromLegalActions:
          v = min(v, self.miniMaxValue(index, nextState, depth - 1, alpha, beta))
          if v <= alpha :
            return v
          beta = min(beta, v)
        return v


#  ______                   _            ____  
# |  ____|                 (_)          |___ \ 
# | |__  __  _____ _ __ ___ _ ___  ___    __) |
# |  __| \ \/ / _ \ '__/ __| / __|/ _ \  |__ < 
# | |____ >  <  __/ | | (__| \__ \  __/  ___) |
# |______/_/\_\___|_| \___|_|___/\___| |____/ 

class ExpectimaxAgent( SearchAgent ):
  """
  Expectimax agent assuming random ghosts.
  """
  def getAction( self, gameState ):

    """
    Returns the minimax action from the current gameState using self.depth
    and self.evaluationFunction.
    """

    trueDepth = gameState.getNumberOfAgents() * self.depth # Warning: use complete moves
    legalActions = gameState.getLegalActions(0)
    
    nextStatesFromLegalActions = [gameState.generateSuccessor(0, action) for action in legalActions]
    # Call recursive minimax
    values = [self.miniMaxValue(0, nextGameState, trueDepth - 1) for nextGameState in nextStatesFromLegalActions] 

    # Get the index of all tie max values
    listOfAllMaxValues = []
    maxValue = max(values)
    # print("max=", maxValue)
    # pause("next")

    for i in range(0, len(values)):
      if values[i] == maxValue:
        listOfAllMaxValues.append(i)
        
    # Random when there is a tie
    idx = random.randint(0, len(listOfAllMaxValues) - 1)
    action = legalActions[listOfAllMaxValues[idx]]
    return action

  def miniMaxValue( self, agentIndex, gameState, depth ):
    if self.isTerminalNode(gameState, depth):
      return self.evaluationFunction(gameState)    
    else:
      legalActions = gameState.getLegalActions(agentIndex)
      nextStatesFromLegalActions = [gameState.generateSuccessor(agentIndex, action) for action in legalActions]
      if agentIndex == 0: # if it's Pacman then it's a max layer
        return max([self.miniMaxValue(1, nextState, depth - 1) for nextState in nextStatesFromLegalActions])
      else: # else if it's a ghost, then it's a min layer
        index = (agentIndex + 1) % gameState.getNumberOfAgents()
        liste = [self.miniMaxValue(index, nextState, depth - 1) for nextState in nextStatesFromLegalActions]
        return sum(liste)/len(liste)


#  ______                   _            _  _   
# |  ____|                 (_)          | || |  
# | |__  __  _____ _ __ ___ _ ___  ___  | || |_ 
# |  __| \ \/ / _ \ '__/ __| / __|/ _ \ |__   _|
# | |____ >  <  __/ | | (__| \__ \  __/    | |  
# |______/_/\_\___|_|  \___|_|___/\___|    |_|  
                                               
def MyEvaluationFunction( currentGameState ):
  """
  Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
  evaluation function.
  Returns an integer that estimates the state vaue.
  """
  
  " *** YOUR CODE HERE ***"
