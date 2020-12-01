import argparse
import re

from . import Candidate, Vote, explain
from .borda import borda
from .borda_even import borda_even
from .borda_exp import borda_exp
from .condorcet import condorcet
from .dowdall import dowdall
from .stv import stv


def main():
    parser = argparse.ArgumentParser(
        prog="votecount",
        description="Calculate the results of a ranked voting election.",
    )
    parser.add_argument(
        "system",
        type=str,
        help=(
            "Vote counting system. One of stv, borda, borda_exp, borda_even, "
            "condorcet, dowdall."
        ),
    )
    parser.add_argument(
        "num_seats",
        type=int,
        help=(
            "Number of seats to fill / winners to pick. Ignored for some "
            "voting systems"
        ),
    )
    parser.add_argument(
        "input_file", help="path to input file with candidates and votes"
    )
    parser.add_argument(
        "--explain", action="store_true", help="explain how the result was arrived at"
    )
    parser.add_argument(
        "--max-per-vote",
        type=int,
        help="Limit the number of listed candidates per vote. Ignored for some "
        "voting systems.",
    )
    parser.add_argument(
        "--weight",
        type=float,
        help=(
            "Custom weighting factor for voting systems such as borda_exp. "
            "Intended to be <1."
        ),
    )
    args = parser.parse_args()

    with open(args.input_file) as input_file:
        input_rows = input_file.readlines()

    candidates_row = input_rows.pop(0).split()
    votes_rows = []
    for row in input_rows:
        row = re.sub(r"^.*:\s*", "", row)  # Remove voter label
        votes_rows.append(row.split())

    candidates = [Candidate(id) for id in candidates_row]
    votes = [Vote(candidates) for candidates in votes_rows]

    system_func = {
        "stv": stv,
        "borda": borda,
        "dowdall": dowdall,
        "borda_exp": borda_exp,
        "borda_even": borda_even,
        "condorcet": condorcet,
    }[args.system]

    winners = system_func(
        args.num_seats,
        candidates,
        votes,
        do_explain=args.explain,
        max_per_vote=args.max_per_vote,
        weight=args.weight,
    )
    explain("                 \n======== RESULTS ========", args.explain)
    for winner in winners:
        print(winner if args.explain else winner.id)


if __name__ == "__main__":
    main()
