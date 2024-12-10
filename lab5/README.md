WUMPUS
======

# Random Agent

```
python3 wumpus.py
```

(_eqv. `./wumpus.py -a DummyAgent -w 4 -s 40 -g 0`)

# Human Agent

Can be used to debug the wumpus world

```
python3 wumpus.py -a HumanAgent -w 10 -g 2

```

# Exercice

## Version: Rational Agent

Running the agent on a 10x10 world with random seed 2:

```
python3 wumpus.py -a RationalAgent -w 10 -g 2
```

Running the agent 10 times without graphical interface (quiet mode)

```
python3 wumpus.py -a RationalAgent -w 10 -g 2 -x 10 -n 10
```

# Version: Learning Agent

Learning the Q-Values during 50 trails (quiet mode) and running the agent 10 times

```
python wumpus.py -a LearningAgent -w 10 -g 1 -x 50 -n 60
```
