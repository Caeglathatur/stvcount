import typing

from . import Candidate, Vote, explain


class BordaCandidate(Candidate):
    def __init__(self, id):
        self.id = id
        self.points = 0

    def __str__(self):
        return f"{self.id}" f"\tpoints={self.points}"


def borda(
    num_seats,
    candidates: typing.List[Candidate],
    votes: typing.List[Vote],
    do_explain=False,
    **kwargs,
) -> typing.List[Candidate]:
    """Borda Count"""

    max_points = kwargs.get("max_per_vote", None) or len(candidates)
    candidates = {c.id: BordaCandidate(c.id) for c in candidates}
    vote_nr = 0
    for vote in votes:
        vote_nr += 1
        explain(
            f"                 \n======== Standings at vote {vote_nr} ========",
            do_explain,
        )
        assign_points = max_points
        for v_candidate in vote.candidates:
            candidates[v_candidate].points += assign_points
            assign_points -= 1
            if assign_points <= 0:
                break
        for candidate in sorted(
            candidates.values(), key=lambda c: c.points, reverse=True
        ):
            explain(candidate, do_explain)

    return list(sorted(candidates.values(), key=lambda c: c.points, reverse=True))
