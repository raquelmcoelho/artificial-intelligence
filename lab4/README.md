Reinforcement-Learner
=====================

# Exercise 1

```
python3 pacman.py -p PacmanQAgent -x 2000 -n 2010 -l smallGrid
```

# Exercise 2

```
python3 pacman.py -p PacmanQAgent -x 2000 -n 2010 -l smallGrid
python3 pacman.py -p PacmanQAgent -x 4000 -n 4010 -l mediumGrid
```

# Exercise 3

```
python3 pacman.py -p ApproximateQAgent -a extractor=SimpleExtractor -x 50 -n 60 -l mediumGrid
python3 pacman.py -p ApproximateQAgent -a extractor=SimpleExtractor -x 50 -n 60 -l mediumClassic
```


# Exercise 4

```
python3 pacman.py -p ApproximateQAgent -a extractor=BetterExtractor -x 50 -n 60 -l contestClassic
```
