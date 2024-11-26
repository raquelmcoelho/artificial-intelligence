# -*- coding: utf-8; mode: python -*-

# ENSICAEN
# École Nationale Supérieure d'Ingénieurs de Caen
# 6 Boulevard Maréchal Juin
# F-14050 Caen Cedex France
#
# Artificial Intelligence 2I1AE1

# @file agents.py
#
# @author Régis Clouard

import copy
import utils

class Agent:
    """
    Abstract class for the agents that implement the various search strategies.
    It is based on the Strategy Design Pattern (abstract method is search()).

    YOU DO NOT NEED TO CHANGE ANYTHING IN THIS CLASS, EVER.
    """
    def search( self ):
        """ This is the method to implement for each specific searcher."""
        raise Exception("Invalid Agent class, search() not implemented")

 #  ______                               _                  __ 
 # |  ____|                             (_)                /_ |
 # | |__    __  __   ___   _ __    ___   _   ___    ___     | |
 # |  __|   \ \/ /  / _ \ | '__|  / __| | | / __|  / _ \    | |
 # | |____   >  <  |  __/ | |    | (__  | | \__ \ |  __/    | |
 # |______| /_/\_\  \___| |_|     \___| |_| |___/  \___|    |_|

class DFS( Agent ):

    def search( self, initial_state ):
        """ Depth-First Search.

        Returns the path as a list of directions among
        { Direction.left, Direction.right, Direction.up, Direction.down }

        """
        open_list = [[ (initial_state, None) ]] # A state is a pair (board, direction)
        closed_list = set([initial_state]) # keep already explored positions

        while open_list:
            # Get the path at the top of the stack (pop() returns the last item of the list)
            current_path = open_list.pop()
            # Get the last place of that path
            current_state, current_direction = current_path[-1]
            # Check if we have reached the goal
            if current_state.is_goal_state():
                # remove the start point and return only the directions.
                return (list (map(lambda x : x[1], current_path[1:])))
            else:
                # Check where we can go from here
                next_steps = current_state.get_successor_states()
                # Add the new paths (one step longer) to the stack
                for state, direction, weight in next_steps:
                    # do not add already explored states
                    if state not in closed_list:
                        # add at the end of the list
                        closed_list.add(state)
                        open_list.append( (current_path + [ (state, direction) ]) )
        return []

class BFS( Agent ):
    
    def search( self, initial_state ):
        """ Breadth-First Search
        
        Returns the path as a list of directions among
        { Direction.left, Direction.right, Direction.up, Direction.down }
        
        Useful methods:
        - state.is_goal_state(): Returns true if the state is a valid goal state.
        - state.get_successor_states(): Returns all states reachable from the state as a list of triplets (state, direction, cost).
        """

        open_list = [[ (initial_state, None) ]] # A state is a pair (board, direction)
        closed_list = set([initial_state]) # keep already explored positions

        while open_list:
            # Get the path at the top of the stack (pop(0) returns the first item of the list)
            current_path = open_list.pop(0)
            # Get the last place of that path
            current_state, current_direction = current_path[-1]
            # Check if we have reached the goal
            if current_state.is_goal_state():
                # remove the start point and return only the directions.
                return (list (map(lambda x : x[1], current_path[1:])))
            else:
                # Check where we can go from here
                next_steps = current_state.get_successor_states()
                # Add the new paths (one step longer) to the stack
                for state, direction, weight in next_steps:
                    # do not add already explored states
                    if state not in closed_list:
                        # add at the end of the list
                        closed_list.add(state)
                        open_list.append( (current_path + [ (state, direction) ]) )
        return []

        # *** YOUR CODE HERE ***
        # Base your work in the above DFS implementation

 #  ______                               _                  ___  
 # |  ____|                             (_)                |__ \ 
 # | |__    __  __   ___   _ __    ___   _   ___    ___       ) |
 # |  __|   \ \/ /  / _ \ | '__|  / __| | | / __|  / _ \     / / 
 # | |____   >  <  |  __/ | |    | (__  | | \__ \ |  __/    / /_ 
 # |______| /_/\_\  \___| |_|     \___| |_| |___/  \___|   |____|

class UCS( Agent ):
    def search( self, initial_state ):
        """ Uniform-Cost Search.

        It returns the path as a list of directions among
        { Direction.left, Direction.right, Direction.up, Direction.down }
        """

        # use a priority queue with the minimum queue.
        from utils import PriorityQueue
        open_list = PriorityQueue()
        open_list.push([(initial_state, None)], 0) # a state is a pair (board, direction)
        closed_list = set([initial_state]) # keep already explored positions

        while not open_list.isEmpty():
            # Get the path at the top of the queue
            current_path, cost = open_list.pop()
            # Get the last place of that path
            current_state, current_direction = current_path[-1]
            # Check if we have reached the goal
            if current_state.is_goal_state():
                return (list (map(lambda x : x[1], current_path[1:])))
            else:
                # Check were we can go from here
                next_steps = current_state.get_successor_states()
                # Add the new paths (one step longer) to the queue
                for state, direction, weight in next_steps:
                    # Avoid loop!
                    if state not in closed_list:
                        closed_list.add(state)
                        open_list.push((current_path + [ (state, direction) ]), cost + weight)
        return []
    
    

class GBFS( Agent ):

    def search( self, initial_state ):
        """ Greedy Best First Search.

        Returns the path as a list of directions among
        { Direction.left, Direction.right, Direction.up, Direction.down }
        
        Useful methods:
        - state.is_goal_state(): Returns true if the state is a valid goal state.
        - state.get_successor_states(): Returns all states reachable from the specified state as a list of triplets (state, direction, cost)
        - state.heuristic(): Returns the heuristic value for the specified state.
        """

        # use a priority queue with the minimum queue.
        from utils import PriorityQueue
        open_list = PriorityQueue()
        open_list.push([(initial_state, None)], initial_state.heuristic()) # a state is a pair (board, direction)
        closed_list = set([initial_state]) # keep already explored positions

        while not open_list.isEmpty():
            # Get the path at the top of the queue
            current_path, cost = open_list.pop()
            # Get the last place of that path
            current_state, current_direction = current_path[-1]
            # Check if we have reached the goal
            if current_state.is_goal_state():
                return (list (map(lambda x : x[1], current_path[1:])))
            else:
                # Check were we can go from here
                next_steps = current_state.get_successor_states()
                # Add the new paths (one step longer) to the queue
                for state, direction, weight in next_steps:
                    # Avoid loop!
                    if state not in closed_list:
                        closed_list.add(state)
                        open_list.push((current_path + [ (state, direction) ]), state.heuristic())
        return []

 #  ______                               _                  ____  
 # |  ____|                             (_)                |___ \ 
 # | |__    __  __   ___   _ __    ___   _   ___    ___      __) |
 # |  __|   \ \/ /  / _ \ | '__|  / __| | | / __|  / _ \    |__ < 
 # | |____   >  <  |  __/ | |    | (__  | | \__ \ |  __/    ___) |
 # |______| /_/\_\  \___| |_|     \___| |_| |___/  \___|   |____/ 


# TODO: fix case 2
class ASS( Agent ):
    def search( self, initial_state ):
        """ A Star Search.

        It returns the path as a list of directions among
        { Direction.left, Direction.right, Direction.up, Direction.down }

        Useful methods:
        - state.is_goal_state(): Returns true if the state is a valid goal state.
        - state.get_successor_states(): Returns all states reachable from the specified state as a list of triplets (state, direction, cost)
        - state.heuristic(): Returns the heuristic value for the specified state.

        """
        
        # use a priority queue with the minimum queue.
        from utils import PriorityQueue
        open_list = PriorityQueue()
        open_list.push([(initial_state, None)], initial_state.heuristic()) # a state is a pair (board, direction)
        closed_list = set([initial_state]) # keep already explored positions

        while not open_list.isEmpty():
            # Get the path at the top of the queue
            current_path, cost = open_list.pop()
            # Get the last place of that path
            current_state, current_direction = current_path[-1]
            # Check if we have reached the goal
            if current_state.is_goal_state():
                return (list (map(lambda x : x[1], current_path[1:])))
            else:
                # Check were we can go from here
                next_steps = current_state.get_successor_states()
                # Add the new paths (one step longer) to the queue
                for state, direction, weight in next_steps:
                    # Avoid loop!
                    if state not in closed_list:
                        closed_list.add(state)
                        open_list.push((current_path + [ (state, direction) ]), (cost + weight + state.heuristic()))
        return []

 #  ______                               _                  _  _   
 # |  ____|                             (_)                | || |  
 # | |__    __  __   ___   _ __    ___   _   ___    ___    | || |_ 
 # |  __|   \ \/ /  / _ \ | '__|  / __| | | / __|  / _ \   |__   _|
 # | |____   >  <  |  __/ | |    | (__  | | \__ \ |  __/      | |  
 # |______| /_/\_\  \___| |_|     \___| |_| |___/  \___|      |_|  

class IDS( Agent ):
    MAX_PATH_LENGTH = 500 # Found in literature
    def search( self, initial_state ):
        """ Iterative Deepening Search.

        Returns the path as a list of directions among
        { Direction.left, Direction.right, Direction.up, Direction.down }

        Useful methods:
        - state.is_goal_state(): Returns true if the state is a valid goal state.
        - state.get_successor_states(): Returns all states reachable from the specified state as a list of triplets (state, direction, cost)
        - state.heuristic(): Returns the heuristic value for the specified state.
        """
        

        
        max_depth = 0

        while(max_depth<self.MAX_PATH_LENGTH):
            open_list = [[ (initial_state, None) ]] # A state is a pair (board, direction)
            closed_list = { initial_state : 0 } # keep already explored positions
            while open_list:
                # Get the path at the top of the stack (pop() returns the last item of the list)
                current_path = open_list.pop()
                depth = len(current_path)
                # Get the last place of that path
                current_state, current_direction = current_path[-1]
                # Check if we have reached the goal
                if current_state.is_goal_state():
                    # remove the start point and return only the directions.
                    return (list (map(lambda x : x[1], current_path[1:])))
                if depth-1 < max_depth :
                    # Check where we can go from here
                    next_steps = current_state.get_successor_states()
                    # Add the new paths (one step longer) to the stack
                    for state, direction, weight in next_steps:
                        # do not add already explored states
                        if state not in closed_list or closed_list[state] > depth-1:
                            # add at the end of the list
                            closed_list[state] = depth
                            open_list.append( (current_path + [ (state, direction) ]) )
                
           
            max_depth += 1

        # max_depth = 0  # Start with depth 0
#
        # while True:
        #     # open_list holds the paths to explore (stack-style DFS)
        #     open_list = [[(initial_state, None)]]  # A state is a pair (state, direction)
        #     # closed_list is a dictionary that tracks the depth at which each state was visited
        #     closed_list = {initial_state: 0}  # Track the start state and its depth (0)

        #     # DFS for the current max depth limit
        #     found_solution = False
        #     while open_list:
        #         current_path = open_list.pop()  # Get the last path from the stack
        #         current_state, current_direction = current_path[-1]  # Get the current state and direction

        #         # Check if the goal has been reached
        #         if current_state.is_goal_state():
        #             # Return only the directions (skip the initial state)
        #             return [direction for _, direction in current_path[1:]]

        #         # If we haven't exceeded the max depth, expand the state
        #         if len(current_path) - 1 < max_depth:
        #             # Get the successors of the current state
        #             next_steps = current_state.get_successor_states()

        #             # Expand the state by adding its successor states
        #             for state, direction, weight in next_steps:
        #                 # Only add the state to the open list if it hasn't been visited at the current depth
        #                 if state not in closed_list or closed_list[state] > len(current_path) - 1:
        #                     closed_list[state] = len(current_path)  # Mark state with the current depth
        #                     open_list.append(current_path + [(state, direction)])  # Add new path to the open list

        #     # If no solution is found at this depth, increase the max_depth and continue the search
        #     max_depth += 1


            
    

    

 #  ______                               _                  _____ 
 # |  ____|                             (_)                | ____|
 # | |__    __  __   ___   _ __    ___   _   ___    ___    | |__  
 # |  __|   \ \/ /  / _ \ | '__|  / __| | | / __|  / _ \   |___ \ 
 # | |____   >  <  |  __/ | |    | (__  | | \__ \ |  __/    ___) |
 # |______| /_/\_\  \___| |_|     \___| |_| |___/  \___|   |____/ 
class IDASS( Agent ):
    MAX_PATH_LENGTH = 500 # Found in literature
    def search( self, initial_state ):
        """ Iterative deepening A*
        
        Returns the path as a list of directions among
        { Direction.left, Direction.right, Direction.up, Direction.down }.

        Useful methods:
        - state.is_goal_state(): Returns true if the state is a valid goal state.
        - state.get_successor_states(): Returns all states reachable from the specified state as a list of triplets (state, direction, cost)
        - state.heuristic(): Returns the heuristic value for the specified state.
        """

        # use a priority queue with the minimum queue.
        from utils import PriorityQueue
        open_list = PriorityQueue()
        open_list.push([(initial_state, None)], 0) # a state is a pair (board, direction)
        closed_list = set([initial_state]) # keep already explored positions

        while not open_list.isEmpty():
            # Get the path at the top of the queue
            current_path, cost = open_list.pop()
            # Get the last place of that path
            current_state, current_direction = current_path[-1]
            # Check if we have reached the goal
            if current_state.is_goal_state():
                return (list (map(lambda x : x[1], current_path[1:])))
            else:
                # Check were we can go from here
                next_steps = current_state.get_successor_states()
                # Add the new paths (one step longer) to the queue
                for state, direction, weight in next_steps:
                    # Avoid loop!
                    if state not in closed_list:
                        closed_list.add(state)
                        open_list.push((current_path + [ (state, direction) ]), (cost + weight + state.heuristic()))
        return []


