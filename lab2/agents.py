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
# @author Régis Clouard.
#

from __future__ import print_function
from grid import Grid
import random
from samples import *
import copy

class Agent:
    """ Abstract class for the various agents.
    
    (Strategy design pattern.)
    YOU DO NOT NEED TO CHANGE ANYTHING IN THIS CLASS, EVER.
    """
    def __init__( self ):
        self.count = 0;
        self.clock = ['|', '/', '-', '\\']

    def increment_count( self):
        self.count += 1;
        self.__display_time()

    def __display_time( self ):
        print("\b\b\b" + self.clock[self.count % 4], end=" ")

    def solve( self, grid ):
        """ This is the method to implement for each specific solver."""
        raise Exception("Invalid CSPSolver class, Solve() not implemented")

def pause( text):
    if sys.version_info.major >= 3:
        input(text)
    else:
        raw_input(text)

def default_heuristic( domains, assignment ):
    """ Picks the first free variable.
    
    @param domains the list of pending values for each unassigned variable.
    @param assigment a partial assignment as a dictionary: variable=value.
    @return a variable (a cell)."""
    return next(iter(domains)) 


#######
####### Backtracking Search Agent
#######    
class BS( Agent ):
    """ Backtracking version of the solver based on simple
    uninformed backtracking search: recursive depth-first search."""

    def solve( self, grid, heuristic_function = default_heuristic ):
        """ Returns a solution as a dictionary of assignment
        eg: {0:'2', 1:'3', ..., 40:'5'}
        or None if no solution is found.

        Notice : this implementation strictly follows the algorithm given in the lecture slides.

        @param grid the initial grid.
        @return a dictionary with a complete assignment or None"""
        self.select_unassigned_variable = heuristic_function
        domains = grid.get_domain_values()
        return self.__recursive_backtracking(grid, domains, {})

    def __recursive_backtracking( self, grid, domains, assignment ):
        """ This private method is externalized to implement a recursive search.
        @return a complete assigment or None. """

        if len(domains) == 0: # All cells set
            return assignment

        self.increment_count()
        #  var = SELECT-UNASSIGNED-VARIABLE(Variables[csp], assignment, csp)
        variable = self.select_unassigned_variable(domains, assignment)
        #  foreach value in ORDER-DOMAIN-VALUES(var, assignment, csp) do
        values = self.__order_domain_values(variable, domains, assignment)
        del domains[variable]
        for value in values:
            # print("Try cell", variable, "with value:", value, "from", values)
            # pause("Next")
            
            #    add {var = value } to assignment
            assignment[variable] = value
            #  if value is consistent with assignment given Constraints[csp] then
            if self.__check_consistency(grid, assignment, variable, value):
                #    result = RECURSIVE-BACKTRACKING(assignment, csp)
                #    Use a deep copy of domains to avoid backtracking issues.
                result = self.__recursive_backtracking(grid, copy.deepcopy(domains), assignment)
                #    if result != failure then return result
                if result is not None:
                    return assignment
            #    remove {var = value} from assignment
            del assignment[variable]

        return None

    def  __order_domain_values( self, variable, domains, assignment ):
        """ 
        Sorts the values by priority using the current heuristic.
        Actually, do nothing, just returns the original list.
        """
        return domains[variable]
    
    def __check_consistency( self, grid, assignment, variable, value ):
        """
        Tests whether the specified value of the variable is consistent with the current state.
        """
        for cell in grid.get_related_cells(variable):
            if cell in assignment and assignment[cell] == value:
                return False
        return True
    
    def is_goal( self, grid, assignment ):
        """ Tests if the assignment is a solution.
        ie. no duplicates in each boxe, line and column.
        
        @param assignment a dictionary with the current assignment.
        @return True if the assignment is complete and consistent.
        """
        for variable, value in assignment.iteritems():
            for cell in grid.get_related_cells(variable):
                if assignment[variable] == assignment[cell]:
                    return False
        return True

#  ______                   _            __ 
# |  ____|                 (_)          /_ |
# | |__  __  _____ _ __ ___ _ ___  ___   | |
# |  __| \ \/ / _ \ '__/ __| / __|/ _ \  | |
# | |____ >  <  __/ | | (__| \__ \  __/  | |
# |______/_/\_\___|_|  \___|_|___/\___|  |_|

class FC( Agent ):
    def solve( self, grid, heuristic_function = default_heuristic ):
        """ Forward Checking.

        Returns a solution as a dictionary of assignment, eg: {0:'2', 1:'3', ...40:'5'}
        or None if no solution is found.
        
        @param grid the current puzzle grid.
        @param heuristic_function the function used to choose the next cell to considered.
        @return a dictionary with a complete assignment or None. """
        #function FC-SEARCH(domains) returns solution/failure
        #  return RECURSIVE-FC-SEARCH({ }, domains)

        self.select_unassigned_variable = heuristic_function
        domains = grid.get_domain_values()
        return self.__recursive_fc_search(grid, domains, {})


    def __recursive_fc_search(self,grid, domains, assignment):
        #function RECURSIVE-FC-SEARCH(assignment, domains) returns solution
        #  IF assignment is complete THEN return assignment
        #  var ← SELECT-UNASSIGNED-VARIABLE(assignment, domains)
        #  FOREACH value in ORDER-DOMAIN-VALUES(var, assignment, domains) DO
        #      add {var = value} to assignment
        #      domains1 ← FORWARD-CHECKING(var, value, copy(domains))
        #	   IF domains1 != failure THEN
        #      		result ← RECURSIVE-FC-SEARCH(assignment, domains1)
        #      		IF result != failure THEN return assignment
        #      remove {var = value} from assignment
        #  return failure
        
        if len(domains) == 0: # All cells set
            return assignment

        self.increment_count()
        #  var = SELECT-UNASSIGNED-VARIABLE(Variables[csp], assignment, csp)
        variable = self.select_unassigned_variable(domains, assignment)
        #  foreach value in ORDER-DOMAIN-VALUES(var, assignment, csp) do
        values = self.__order_domain_values(variable, domains, assignment)
        del domains[variable]
        for value in values:
            # print("Try cell", variable, "with value:", value, "from", values)
            # pause("Next")
            
            #    add {var = value } to assignment
            assignment[variable] = value
            
            domains1 = self.__forward_checking(grid, variable, value, copy.deepcopy(domains))
            #  if value is consistent with assignment given Constraints[csp] then
            if domains1 is not None:
                #    result = RECURSIVE-BACKTRACKING(assignment, csp)
                #    Use a deep copy of domains to avoid backtracking issues.
                result = self.__recursive_fc_search(grid, domains1, assignment)
                #    if result != failure then return result
                if result is not None:
                    return assignment
            #    remove {var = value} from assignment
            del assignment[variable]

        return None
    

    def __forward_checking(self, grid, variable, value, domains):

        #function FORWARD-CHECKING(var,value,domains) returns domains/failure
        #  FOREACH xi in domains whose values are constrained by var
        #    IF xi=v is inconsistent with var=value THEN
        #		remove v from the domain of xi in domains
        #		IF the domain of xi is empty THEN return failure
        #  return domains

        for cell in grid.get_related_cells(variable):
            if cell in domains and value in domains[cell]:
                domains[cell].remove(value)
                if len(domains[cell]) == 0 :
                    return None
        return domains
        
    def  __order_domain_values( self, variable, domains, assignment ):
        """ 
        Sorts the values by priority using the current heuristic.
        Actually, do nothing, just returns the original list.
        """
        return domains[variable]
    
    
   



#  ______                   _            ___  
# |  ____|                 (_)          |__ \ 
# | |__  __  _____ _ __ ___ _ ___  ___     ) |
# |  __| \ \/ / _ \ '__/ __| / __|/ _ \   / / 
# | |____ >  <  __/ | | (__| \__ \  __/  / /_ 
# |______/_/\_\___|_|  \___|_|___/\___| |____|
 
def my_heuristic( domains, assignment):
    """ A clever heuristic for choosing the next cell to consider.
    
    @param domains the list of pending values for each unassigned variable.
    @param assigment a partial assignment as a dictionary: variable=value.
    @return variable"""

    min = float("inf")
    minKey = None
    for key, value in domains.items():
        if len(value) < min :
            min = len(value)
            minKey = key
    return minKey




#  ______                   _            ____  
# |  ____|                 (_)          |___ \ 
# | |__  __  _____ _ __ ___ _ ___  ___    __) |
# |  __| \ \/ / _ \ '__/ __| / __|/ _ \  |__ < 
# | |____ >  <  __/ | | (__| \__ \  __/  ___) |
# |______/_/\_\___|_| \___|_|___/\___| |____/ 

class AC3( Agent ):
    def solve( self, grid, heuristic_function = default_heuristic ):
        """ Arc Consistency as preprocessing.
        Returns the domain of values after applying
        the arc consistency technique.

        @param grid the current puzzle grid.
        @param heuristic_function the function used to choose the next cell to considered.
        @return a list or None."""

        self.__heuristic_function = heuristic_function
        domains = grid.get_domain_values()
        # Prune the domain of each variable
        return self.__AC3(grid, domains)

    def __AC3( self, grid, domains ):
        """ Prunes the domain of variables. """

        queue = grid.get_related_cells()
        while queue:
            xi, xj = queue






#  ______                   _            _  _   
# |  ____|                 (_)          | || |  
# | |__  __  _____ _ __ ___ _ ___  ___  | || |_ 
# |  __| \ \/ / _ \ '__/ __| / __|/ _ \ |__   _|
# | |____ >  <  __/ | | (__| \__ \  __/    | |  
# |______/_/\_\___|_|  \___|_|___/\___|    |_|  

class AC_FC( Agent ):
    def solve( self, grid, heuristic_function = default_heuristic ):
        """ Forward Checking with Arc Consistency as preprocessing.

        Returns a solution as a dictionary of assignment, eg: {0:'2', 1:'3', ...40:'5'}
        or None if no solution is found.
        
        @param grid the current puzzle grid.
        @param heuristic_function the function used to choose the next cell to considered.
        @return a dictionary with a complete assignment or None."""

        "*** YOUR CODE HERE ***"

#  ______                   _            _____ 
# |  ____|                 (_)          | ____|
# | |__  __  _____ _ __ ___ _ ___  ___  | |__  
# |  __| \ \/ / _ \ '__/ __| / __|/ _ \ |___ \ 
# | |____ >  <  __/ | | (__| \__ \  __/  ___) |
# |______/_/\_\___|_|  \___|_|___/\___| |____/ 
                                              
class MAC( Agent ):
    def solve( self, grid, heuristic_function = default_heuristic ):
        """ Maintaining Arc Consistency.

        Returns a solution as a dictionary of assignment, eg: {0:'2', 1:'3', ...40:'5'}
        or None if no solution is found.
        
        @param grid the current puzzle grid.
        @param heuristic_function the function used to choose the next cell to considered.
        @return a dictionary with a complete assignment or None."""

        "*** YOUR CODE HERE ***"
