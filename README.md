stvcount
========

A simple and very rough CLI tool for calculating the results of some half-assed
interpretation of "Single Transferable Vote with Condorcet Loser Elimination"
(STV-CLE) elections. Hacked into existence in one evening.

Python 3.8

## Usage

```sh
python -m stvcount <number of seats> <path to input file>
```

where "input file" is a simple text file where the first row lists all candidates, followed by all the votes/ballots, one vote per line, e.g.

```
1 2 3 4 5 6 7 8 9
4 5 3
4 8 9 1
2 5 6
8 1 7 6
3 4 8 7
7 4 8 2 5 6
3 5 8 6 9 1 2
```
