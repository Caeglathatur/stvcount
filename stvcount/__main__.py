import argparse
import re
import sys
import typing
from copy import deepcopy


EXPLAIN = False


def explain(string):
    global EXPLAIN
    if EXPLAIN:
        print(string)


class Candidate:
    def __init__(self, id):
        self.id = id
        self.num_votes = 0
        self.proportion_of_votes = 0
        self.condorcet_score = 0

    def __repr__(self):
        return f"<Candidate: {self.id} - {self.proportion_of_votes} - {self.condorcet_score}>"

    def __str__(self):
        return str(self.id)


class Vote:
    def __init__(self, candidates):
        self.candidates = candidates

    def __repr__(self):
        return f"<Vote: {self.candidates}>"


def condorcet_pair(
    candidate1: Candidate, candidate2: Candidate, votes: typing.List[Vote]
):
    # Remove all candidates from votes for other candidates
    candidates = {candidate1.id: candidate1, candidate2.id: candidate2}
    for vote in votes:
        vote.candidates = list(filter(lambda c: c in candidates, vote.candidates))

    # Remove empty votes
    votes = list(filter(lambda v: len(v.candidates) > 0, votes))

    # Reset tallies
    for candidate in candidates.values():
        candidate.num_votes = 0
        candidate.proportion_of_votes = 0

    # Count votes
    for vote in votes:
        try:
            candidate_id = vote.candidates[0]
        except IndexError:
            raise RuntimeError("should never happen; no empty votes should exist here")
        candidates[candidate_id].num_votes += 1

    if candidate1.num_votes > candidate2.num_votes:
        explain(
            f"\t{candidate1.id} ({candidate1.num_votes}, WIN)\tvs\t"
            f"{candidate2.id} ({candidate2.num_votes})"
        )
        candidate1.condorcet_score += 1
    elif candidate2.num_votes > candidate1.num_votes:
        explain(
            f"\t{candidate1.id} ({candidate1.num_votes})\tvs\t"
            f"{candidate2.id} ({candidate2.num_votes}, WIN)"
        )
        candidate2.condorcet_score += 1
    else:
        explain(
            f"\t{candidate1.id} ({candidate1.num_votes})\tvs\t"
            f"{candidate2.id} ({candidate2.num_votes})\tTIED"
        )


def condorcet(candidates: typing.List[Candidate], votes: typing.List[Vote]):
    explain("Condorcet pairings:")
    for i, candidate1 in enumerate(candidates):
        for j in range(i + 1, len(candidates)):
            candidate2 = candidates[j]
            # print(candidate1, candidate2)
            condorcet_pair(candidate1, candidate2, deepcopy(votes))


def find_lowest_condorcet(candidates: typing.List[Candidate]):
    return (
        sorted(candidates, key=lambda c: c.condorcet_score)[0] if candidates else None
    )


def find_lowest_proportion(candidates: typing.List[Candidate]):
    return (
        sorted(candidates, key=lambda c: c.proportion_of_votes)[0]
        if candidates
        else None
    )


def stv_cle(
    num_seats, candidates: typing.Dict[id, Candidate], votes: typing.List[Vote]
):
    """Single Transferable Vote with Condorcet Loser Elimination"""

    victory_quota = 1 / num_seats
    winners = []

    condorcet(list(candidates.values()), deepcopy(votes))

    round_ = 0
    while votes:
        round_ += 1

        # Reset tallies
        for candidate in candidates.values():
            candidate.num_votes = 0
            candidate.proportion_of_votes = 0

        # Count votes and calculate proportions
        for vote in votes:
            try:
                candidate_id = vote.candidates[0]
            except IndexError:
                raise RuntimeError(
                    "should never happen; no empty votes should exist here"
                )
            candidates[candidate_id].num_votes += 1
        for candidate in candidates.values():
            candidate.proportion_of_votes = candidate.num_votes / len(votes)

        explain(f"                 \n======== ROUND {round_} ========")
        explain("Standings:")
        explain("\tCandidate\tProportion of votes\tCondorcet score")
        for candidate in candidates.values():
            explain(
                f"\t{candidate}\t{candidate.proportion_of_votes}\t{candidate.condorcet_score}"
            )

        # Find new winners
        new_winners = []
        for candidate in candidates.values():
            if candidate.proportion_of_votes >= victory_quota:
                new_winners.append(candidate)

        # Is there a winner?
        if new_winners:
            # Yes
            explain(
                f"{len(new_winners)} candidates meet the victory quota of {victory_quota}:"
            )
            for winner in new_winners:
                explain(f"\t{winner.id} ({winner.proportion_of_votes})")
            # Remove excess winners based on condorcet score
            num_tied_for_last = len(winners) + len(new_winners) - num_seats
            if num_tied_for_last > 0:
                explain(
                    "There are more winners this round than there are seats left. Excluding those with the lowest "
                    "condorcet scores:"
                )
                for i in range(num_tied_for_last):
                    lowest = find_lowest_condorcet(new_winners)
                    lowest_proportion = find_lowest_proportion(
                        new_winners
                    ).proportion_of_votes
                    assert lowest.proportion_of_votes <= lowest_proportion
                    explain(f"\t{lowest}")
                    new_winners.remove(lowest)
            explain(
                "The following candidates have been declared winners in this round:"
            )
            for winner in sorted(
                new_winners, key=lambda c: c.proportion_of_votes, reverse=True
            ):
                winners.append(candidates.pop(winner.id))
                explain(f"\t{winner.id}")

            if len(winners) >= num_seats:
                # All seats filled
                explain(f"All {num_seats} seats have been filled.")
                break
            # Remove new winners from votes
            for vote in votes:
                for winner in new_winners:
                    if winner.id in vote.candidates:
                        vote.candidates.remove(winner.id)
        else:
            # No, eliminate candidate with lowest condorcet score
            last_candidate = find_lowest_condorcet(candidates.values())
            explain(
                f"No candidates meet the victory quota of {victory_quota}. Excluding the "
                f"candidate with the lowest condorcet score:\n\t{last_candidate.id} "
                f"({last_candidate.condorcet_score})"
            )
            lowest_proportion = find_lowest_proportion(
                candidates.values()
            ).proportion_of_votes
            assert last_candidate.proportion_of_votes <= lowest_proportion
            candidates.pop(last_candidate.id)
            # Remove excluded from votes
            for vote in votes:
                if last_candidate.id in vote.candidates:
                    vote.candidates.remove(last_candidate.id)

        # Remove empty votes
        votes = list(filter(lambda v: len(v.candidates) > 0, votes))
        explain(
            f"{num_seats - len(winners)} of {num_seats} seats are still to be filled."
        )

    return winners


def main():
    parser = argparse.ArgumentParser(
        prog="stvcount", description="Calculate the results of an STV-CLE election."
    )
    parser.add_argument(
        "num_seats", type=int, help="number of seats to fill / winners to pick"
    )
    parser.add_argument(
        "input_file", help="path to input file with candidates and votes"
    )
    parser.add_argument(
        "--explain", action="store_true", help="explain how the result was arrived at"
    )
    args = parser.parse_args()

    global EXPLAIN
    EXPLAIN = args.explain

    with open(args.input_file) as input_file:
        input_rows = input_file.readlines()

    candidates_row = input_rows.pop(0).split()
    votes_rows = []
    for row in input_rows:
        row = re.sub(r"^.*:\s*", "", row)  # Remove voter label
        votes_rows.append(row.split())

    candidates = {id: Candidate(id) for id in candidates_row}
    votes = [Vote(candidates) for candidates in votes_rows]

    winners = stv_cle(args.num_seats, candidates, votes)
    explain("                 \n======== WINNERS ========")
    for winner in winners:
        print(winner)


if __name__ == "__main__":
    main()
