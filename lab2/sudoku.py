#!/usr/bin/python3
# -*- coding: utf-8; mode: python -*-
#
# ENSICAEN
# École Nationale Supérieure d'Ingénieurs de Caen
# 6 Boulevard Maréchal Juin
# F-14050 Caen Cedex France
#
# Artificial Intelligence 2I1AE1
#

#
# @file sudoku.py
#
# @author Régis Clouard.
#

from __future__ import print_function

import sys
from grid import Grid
import samples
from agents import Agent, AC3
import signal

WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'

class TimeoutFunctionException( Exception ):
    """Exception to raise on a timeout"""
    pass

class TimeoutFunction:

    def __init__( self, function, timeout ):
        "timeout must be at least 1 second."
        self.timeout = timeout
        self.function = function

    def handle_timeout( self, signum, frame ):
        raise TimeoutFunctionException()

    def __call__( self, *args ):
        if not 'SIGALRM' in dir(signal):
            return self.function(*args)
        old = signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.timeout)
        try:
            result = self.function(*args)
        finally:
            signal.signal(signal.SIGALRM, old)
        signal.alarm(0)
        return result

def run_agent( agent, grid, timeout, mute, correction, function=None ):
    """ The real main. """
    if function:
        gridInstance = Grid(grid, agent, function)
    else:
        gridInstance = Grid(grid, agent)
    if not mute:
        print("Initial Sudoku:")
        gridInstance.display()

    timed_func = TimeoutFunction(gridInstance.solve, timeout)
    try:
        result = timed_func()
    except TimeoutFunctionException as ex:
        result = None
        print("Error #1: time out", ex)

    if correction:
        if isinstance(agent, AC3):
            groundtruth = [['1'], ['3', '6', '8', '9'], ['5'], ['2', '8'], ['7'], ['2', '8', '9'], ['4'], ['3', '6', '9'], ['2', '9'], ['7', '8', '9'], ['3', '6', '7', '8', '9'], ['4'], ['1', '2', '8'], ['1', '8'], ['5'], ['3', '7', '9'], ['3', '6', '7', '9'], ['2', '9'], ['2'], ['7', '9'], ['7', '9'], ['3'], ['6'], ['4'], ['5', '7', '9'], ['8'], ['1'], ['7', '8', '9'], ['2', '7', '8', '9'], ['7', '8', '9'], ['1', '4', '5', '8'], ['3'], ['1', '8'], ['1', '5', '7', '9'], ['1', '4', '5', '7', '9'], ['6'], ['4'], ['5'], ['1'], ['6'], ['9'], ['7'], ['8'], ['2'], ['3'], ['3'], ['6', '7', '8', '9'], ['6', '7', '8', '9'], ['1', '4', '5', '8'], ['2'], ['1', '8'], ['1', '5', '7', '9'], ['1', '4', '5', '7', '9'], ['4', '9'], ['6'], ['4'], ['3', '8', '9'], ['7'], ['1', '8'], ['1', '2', '3', '8'], ['1', '3', '9'], ['1', '3', '9'], ['5'], ['5', '7', '8'], ['1', '3', '7', '8'], ['3', '7', '8'], ['9'], ['1', '5', '8'], ['1', '3', '6', '8'], ['2'], ['1', '3', '4'], ['4', '8'], ['5', '8', '9'], ['1', '3', '8', '9'], ['2'], ['1', '5', '8'], ['4'], ['1', '3', '8'], ['6'], ['1', '3', '9'], ['7']]
            if result == groundtruth:
                print("Arc consistency: SUCCESS")
            else:
                print(FAIL + "/!\ Arc consistency: FAILURE" + ENDC)
    if result:
        if gridInstance.is_valid():
            print("\nSudoku Solved.")
            if not mute:
                gridInstance.display()
        else:
            if not mute:
                gridInstance.display_partial()
    else:
         print(FAIL + "/!\ No solution. Sudoku unsolved!" + ENDC)
    print("\nStatictics:")
    print("    - Number of explored states: %3d" % (gridInstance.count))
    print("    - Total computation time   : %3.1fs" % (gridInstance.computation_time))

def default( str ):
    return str + ' [Default: %default]'

def read_command( argv ):
    """ Processes the command used to run sudoku from the command line. """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python sudoku.py <options>
    EXAMPLES:   python sudoku.py --agent BacktrackingCSPAgent --puzzle puzzle2
                OR  python sudoku.py -a BacktrackingCSPAgent -p puzzle2
                    - solve puzzle 2 with the naive agent
    """
    parser = OptionParser(usageStr)
    
    parser.add_option('-a', '--agent', dest='agent',
                      help=default('the agent to use'),
                      metavar='TYPE', default='BS')
    parser.add_option('-p', '--puzzle', dest='grid',
                      help='The puzzle to solve', default='puzzle0')
    parser.add_option('-f', '--function', dest='function',
                      help='The heuristic to use', default=None)
    parser.add_option('-t', '--timeout', dest='timeout',
                      help=default('Maximum search time'), default=300)
    parser.add_option('-m', '--mute', action='store_true', dest='mute',
                      help='Display only results', default=False)
    parser.add_option('-c', '--correction', action='store_true', dest='correction',
                      help='For evalution purpose only', default=False)
    
    options, otherjunk = parser.parse_args(argv)

    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    args = dict()
    
    # Choose a Sudoku agent
    try:
        module = __import__('agents')
        if options.agent in dir(module):
            agent = getattr(module, options.agent)
            args['agent'] = agent()
        else:
            raise Exception('Unknown agent: ' + options.agent)
    except ImportError:
        raise Exception('No file agents.py')
    
    # Choose a puzzle
    try:
        module = __import__('samples')
        if options.grid in dir(module):
            args['grid'] = getattr(module, options.grid)
        else:
            raise Exception('Unknown puzzle: ' + options.grid)
    except ImportError:
        raise Exception('No file samples.py')

    args['timeout'] = int(options.timeout)
    args['mute'] = options.mute
    args['correction'] = options.correction

    # Choose a heuristic
    if options.function!= None:
        if options.function=="correction":
            args['function'] = testFunction
        else:
            try:
                module = __import__('agents')
                if options.function in dir(module):
                    args['function'] = getattr(module, options.function)
                else:
                    raise Exception('Unknown heuristic: ' + options.function)
            except ImportError:
                raise Exception('No file agents.py')
    return args

if __name__ == '__main__':
    """ The main function called when sudoku.py is run
    from the command line:

    > python sudoku.py

    See the usage string for more details.

    > python sudoku.py --help
    > python sudoku.py -h """
    args = read_command( sys.argv[1:] ) # Get game components based on input
    print("\n-------------------------------------------------------")
    for arg in sys.argv:
        print(arg, end= " ")
    print("\n-------------------------------------------------------")
    run_agent( **args )
