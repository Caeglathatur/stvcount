import typing
from copy import deepcopy
from statistics import mean

from . import Candidate, Vote, explain


class STVCandidate(Candidate):
    def __init__(self, id):
        super().__init__(id)
        self.num_votes = 0
        self.proportion_of_votes = 0
        self.condorcet_score = 0
        self.avg_index = None
        self.won_in_round = None

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


def _condorcet_pair(
    candidate1: STVCandidate,
    candidate2: STVCandidate,
    votes: typing.List[Vote],
    do_explain,
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
            f"{candidate2.id} ({candidate2.num_votes})",
            do_explain,
        )
        candidate1.condorcet_score += 1
    elif candidate2.num_votes > candidate1.num_votes:
        explain(
            f"\t{candidate1.id} ({candidate1.num_votes})\tvs\t"
            f"{candidate2.id} ({candidate2.num_votes}, WIN)",
            do_explain,
        )
        candidate2.condorcet_score += 1
    else:
        explain(
            f"\t{candidate1.id} ({candidate1.num_votes})\tvs\t"
            f"{candidate2.id} ({candidate2.num_votes})\tTIED",
            do_explain,
        )


def _condorcet(
    candidates: typing.List[STVCandidate], votes: typing.List[Vote], do_explain
):
    explain("Condorcet pairings:", do_explain)
    for i, candidate1 in enumerate(candidates):
        for j in range(i + 1, len(candidates)):
            candidate2 = candidates[j]
            # print(candidate1, candidate2)
            _condorcet_pair(candidate1, candidate2, deepcopy(votes), do_explain)


def _avg_index(
    candidates: typing.List[STVCandidate], votes: typing.List[Vote], do_explain
):
    explain("Average indexes (i.e. positions) in votes:", do_explain)
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
        explain(f"\t{candidate.id}\t{candidate.avg_index}", do_explain)


def _find_candidate_to_eliminate(candidates: typing.List[STVCandidate]) -> STVCandidate:
    return sorted(
        candidates,
        key=lambda c: (c.proportion_of_votes, c.condorcet_score, -c.avg_index),
    )[0]


def stv(
    num_seats,
    candidates: typing.List[Candidate],
    votes: typing.List[Vote],
    do_explain=False,
) -> typing.List[Candidate]:
    """Single Transferable Vote"""

    candidates = {c.id: STVCandidate(c.id) for c in candidates}

    victory_quota = 1 / num_seats
    winners = []

    _avg_index(list(candidates.values()), votes, do_explain)
    _condorcet(list(candidates.values()), deepcopy(votes), do_explain)

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

        explain(f"                 \n======== ROUND {round_} ========", do_explain)
        explain("Standings:", do_explain)
        # explain("\tCandidate\tProportion of votes\tCondorcet score\tAverage index")
        for candidate in sorted(
            candidates.values(),
            key=lambda c: (c.proportion_of_votes, c.condorcet_score, -c.avg_index),
            reverse=True,
        ):
            explain(f"\t{candidate}", do_explain)

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
                f"{victory_quota}:",
                do_explain,
            )
            for winner in new_winners:
                explain(f"\t{winner}", do_explain)
            # Remove excess winners based on condorcet score
            num_tied_for_last = len(winners) + len(new_winners) - num_seats
            if num_tied_for_last > 0:
                explain(
                    "There are more winners this round than there are seats left. "
                    "Eliminating those with the lowest proportions of votes, "
                    "lowest condorcet scores and highest average indexes:",
                    do_explain,
                )
                for i in range(num_tied_for_last):
                    eliminate = _find_candidate_to_eliminate(new_winners)
                    explain(f"\t{eliminate}", do_explain)
                    new_winners.remove(eliminate)
            explain(
                "The following candidates have been declared winners in this round:",
                do_explain,
            )
            for winner in sorted(
                new_winners,
                key=lambda c: (c.proportion_of_votes, c.condorcet_score, -c.avg_index),
                reverse=True,
            ):
                winners.append(candidates.pop(winner.id))
                explain(f"\t{winner}", do_explain)
                winner.won_in_round = round_

            if len(winners) >= num_seats:
                # All seats filled
                explain(f"All {num_seats} seats have been filled.", do_explain)
                break
            # Remove new winners from votes
            for vote in votes:
                for winner in new_winners:
                    if winner.id in vote.candidates:
                        vote.candidates.remove(winner.id)
        else:
            # No, eliminate candidate with lowest condorcet score
            eliminate = _find_candidate_to_eliminate(candidates.values())
            explain(
                f"No candidates meet the victory quota of {victory_quota}. "
                "Eliminating the candidate with the lowest proportion of votes, "
                f"lowest condorcet score and highest average index:\n"
                f"\t{eliminate}",
                do_explain,
            )
            candidates.pop(eliminate.id)
            # Remove eliminated from votes
            for vote in votes:
                if eliminate.id in vote.candidates:
                    vote.candidates.remove(eliminate.id)

        # Remove empty votes
        votes = list(filter(lambda v: len(v.candidates) > 0, votes))
        explain(
            f"{num_seats - len(winners)} of {num_seats} seats are still to be filled.",
            do_explain,
        )

    if len(candidates) <= num_seats - len(winners):
        explain(
            "Remaining candidates cannot meet the quota, but since there are enough "
            "seats left for them, they will be declared winners:",
            do_explain,
        )
        for candidate in sorted(
            candidates.values(),
            key=lambda c: (c.proportion_of_votes, c.condorcet_score, -c.avg_index),
            reverse=True,
        ):
            winners.append(candidates.pop(candidate.id))
            explain(f"\t{candidate}", do_explain)
            candidate.won_in_round = round_

    return winners
