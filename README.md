votecount
=========

A simple CLI tool for calculating the results of some interpretation of "Single
Transferable Vote" (STV) elections. Loser elimination is done based on fewest
top-choice votes, with lowest condorcet score used as a primary tiebreaker and
highest average position in votes used as a secondary tiebreaker.

Python 3.8

## Usage

```sh
python -m votecount [-h] [--explain] <system> <number of seats> <path to input file>
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

The candidate identifiers don't need to be numeric. Any UTF-8 strings without whitespaces will do.

Lines with votes can optionally be labeled. They are just for convenience and are simply ignored by the program.

```
voter 1: candidate2 candidate1 candidate3
```

If the program is run with the flag `--explain`, it will provide a detailed
step-by-step explanation of how the result was arrived at.

## Run tests

```sh
python -m votecount.tests
```

## License

MIT License

Copyright (c) 2020 Caeglathatur

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
