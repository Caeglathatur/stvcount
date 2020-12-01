import typing
from copy import deepcopy

from . import Candidate, Vote, explain


class CondorcetCandidate(Candidate):
    def __init__(self, id):
        self.id = id
        self.condorcet_score = 0

    def __str__(self):
        return f"{self.id}\tcondorcet={self.condorcet_score}"


def _condorcet_pair(
    candidate1: CondorcetCandidate,
    candidate2: CondorcetCandidate,
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


def condorcet(
    num_seats,
    candidates: typing.List[Candidate],
    votes: typing.List[Vote],
    do_explain=False,
    **kwargs,
) -> typing.List[Candidate]:
    """Condorcet Count"""

    candidates = [CondorcetCandidate(c.id) for c in candidates]

    explain("Condorcet pairings:", do_explain)
    for i, candidate1 in enumerate(candidates):
        for j in range(i + 1, len(candidates)):
            candidate2 = candidates[j]
            _condorcet_pair(candidate1, candidate2, deepcopy(votes), do_explain)

    return list(sorted(candidates, key=lambda c: c.condorcet_score, reverse=True))
