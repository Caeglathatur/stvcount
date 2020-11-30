import argparse
import re
import typing
from copy import deepcopy
from statistics import mean

global_explain = False


def explain(string):
    global global_explain
    if global_explain:
        print(string)


class Candidate:
    def __init__(self, id):
        self.id = id
        self.num_votes = 0
        self.proportion_of_votes = 0
        self.condorcet_score = 0
        self.avg_index = None
        self.won_in_round = None

    def __repr__(self):
        return f"<Candidate: {self.id}>"

    def __str__(self):
        return (
            f"{self.id}"
            f"\tvotes={self.proportion_of_votes}"
            f"\tcondorcet={self.condorcet_score}"
            f"\tavg_index={self.avg_index}"
            + (
                f"\twon_in_round={self.won_in_round}"
                if self.won_in_round is not None
                else ""
            )
        )


class Vote:
    def __init__(self, candidates: typing.List[str]):
        seen = set()
        self.candidates: typing.List[str] = []
        for c in candidates:
            if c in seen:
                raise RuntimeError(
                    f'Found vote in which "{c}" appears more than once: '
                    f"{' '.join(candidates)}"
                )
            seen.add(c)
            self.candidates.append(c)

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


def avg_index(candidates: typing.List[Candidate], votes: typing.List[Vote]):
    explain("Average indexes (i.e. positions) in votes:")
    for candidate in candidates:
        candidate_indexes = []
        for vote in votes:
            try:
                idx = vote.candidates.index(candidate.id)
            except ValueError:
                # Candidate not listed in vote
                idx_of_first_not_listed = len(vote.candidates)
                idx_of_last_not_listed = len(candidates) - 1
                idx = (idx_of_first_not_listed + idx_of_last_not_listed) / 2
            candidate_indexes.append(idx)
        candidate.avg_index = mean(candidate_indexes)
        explain(f"\t{candidate.id}\t{candidate.avg_index}")


def find_candidate_to_eliminate(candidates: typing.List[Candidate]) -> Candidate:
    return sorted(
        candidates,
        key=lambda c: (c.proportion_of_votes, c.condorcet_score, -c.avg_index),
    )[0]


def stv(num_seats, candidates: typing.List[Candidate], votes: typing.List[Vote]):
    """Single Transferable Vote"""

    candidates = {c.id: c for c in candidates}

    victory_quota = 1 / num_seats
    winners = []

    avg_index(list(candidates.values()), votes)
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
        # explain("\tCandidate\tProportion of votes\tCondorcet score\tAverage index")
        for candidate in sorted(
            candidates.values(),
            key=lambda c: (c.proportion_of_votes, c.condorcet_score, -c.avg_index),
            reverse=True,
        ):
            explain(f"\t{candidate}")

        # Find new winners
        new_winners = []
        for candidate in candidates.values():
            if candidate.proportion_of_votes >= victory_quota:
                new_winners.append(candidate)

        # Is there a winner?
        if new_winners:
            # Yes
            explain(
                f"{len(new_winners)} candidates meet the victory quota of "
                f"{victory_quota}:"
            )
            for winner in new_winners:
                explain(f"\t{winner}")
            # Remove excess winners based on condorcet score
            num_tied_for_last = len(winners) + len(new_winners) - num_seats
            if num_tied_for_last > 0:
                explain(
                    "There are more winners this round than there are seats left. "
                    "Eliminating those with the lowest proportions of votes, "
                    "lowest condorcet scores and highest average indexes:"
                )
                for i in range(num_tied_for_last):
                    eliminate = find_candidate_to_eliminate(new_winners)
                    explain(f"\t{eliminate}")
                    new_winners.remove(eliminate)
            explain(
                "The following candidates have been declared winners in this round:"
            )
            for winner in sorted(
                new_winners,
                key=lambda c: (c.proportion_of_votes, c.condorcet_score, -c.avg_index),
                reverse=True,
            ):
                winners.append(candidates.pop(winner.id))
                explain(f"\t{winner}")
                winner.won_in_round = round_

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
            eliminate = find_candidate_to_eliminate(candidates.values())
            explain(
                f"No candidates meet the victory quota of {victory_quota}. "
                "Eliminating the candidate with the lowest proportion of votes, "
                f"lowest condorcet score and highest average index:\n"
                f"\t{eliminate}"
            )
            candidates.pop(eliminate.id)
            # Remove eliminated from votes
            for vote in votes:
                if eliminate.id in vote.candidates:
                    vote.candidates.remove(eliminate.id)

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

    global global_explain
    global_explain = args.explain

    with open(args.input_file) as input_file:
        input_rows = input_file.readlines()

    candidates_row = input_rows.pop(0).split()
    votes_rows = []
    for row in input_rows:
        row = re.sub(r"^.*:\s*", "", row)  # Remove voter label
        votes_rows.append(row.split())

    candidates = [Candidate(id) for id in candidates_row]
    votes = [Vote(candidates) for candidates in votes_rows]

    winners = stv(args.num_seats, candidates, votes)
    explain("                 \n======== WINNERS ========")
    for winner in winners:
        print(winner if global_explain else winner.id)


if __name__ == "__main__":
    main()
