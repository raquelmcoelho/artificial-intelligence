Adversarial Search Problem with Pac-Man
=======================================

```
./pacman.py
```

# Exercise 1

```
python3 pacman.py -p MinimaxAgent1 -l minimaxClassic -a depth=3 -k 1
python3 pacman.py -p MinimaxAgent1 -l smallClassic -a depth=3 -k 1
python3 pacman.py -p MinimaxAgent1 -l minimaxClassic -a depth=3 -k 1 -q -n 10


python3 pacman.py -p MinimaxAgentN -l minimaxClassic -a depth=3 -k 3 --frameTime=0.5
python3 pacman.py -p MinimaxAgentN -l smallClassic -a depth=3 -k 3
python3 pacman.py -p MinimaxAgentN -l minimaxClassic -a depth=3 -k 3 -q -n 10
```

# Exercise 2

```
python3 pacman.py -p AlphaBetaAgent -l smallClassic -a depth=3 -k 2
python3 pacman.py -p AlphaBetaAgent -l smallClassic -a depth=4 -k 3
python3 pacman.py -p AlphaBetaAgent -l minimaxClassic -a depth=7 -k 2
python3 pacman.py -p AlphaBetaAgent -l minimaxClassic -a depth=7 -k 2
```

# Exercise 3

```
python3 pacman.py -p MinimaxAgentN -l trappedClassic -a depth=3 -q -n 10
python3 pacman.py -p ExpectimaxAgent -l trappedClassic -a depth=3 -q -n 10

python3 pacman.py -p ExpectimaxAgent -l smallClassic -a depth=3 -k 3
python3 pacman.py -p ExpectimaxAgent -l minimaxClassic -a depth=4 -k 2
python3 pacman.py -p ExpectimaxAgent -l minimaxClassic -a depth=4 -k 2 -q -n 10
```

# Exercise 4

```
python3 pacman.py -p ExpectimaxAgent -l minimaxClassic -a evalFn=MyEvaluationFunction,depth=2 -k 3
python3 pacman.py -p ExpectimaxAgent -l minimaxClassic -a evalFn=MyEvaluationFunction,depth=2 -k 3 -q -n 100
python3 pacman.py -p AlphaBetaAgent -l smallClassic -a evalFn=MyEvaluationFunction,depth=4 -k 3
python3 pacman.py -p ExpectimaxAgent -l minimaxClassic -a evalFn=MyEvaluationFunction,depth=4 -k 3 -q -n 10
python3 pacman.py -p ExpectimaxAgent -l mediumClassic -a evalFn=MyEvaluationFunction,depth=3 -k 3
```
