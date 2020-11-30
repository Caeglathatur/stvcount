import typing

from . import Candidate, Vote, explain


class BordaCandidate(Candidate):
    def __init__(self, id):
        self.id = id
        self.points = 0

    def __str__(self):
        return f"{self.id}" f"\tpoints={self.points}"


def borda_exp(
    num_seats,
    candidates: typing.List[Candidate],
    votes: typing.List[Vote],
    do_explain=False,
    **kwargs,
) -> typing.List[Candidate]:
    """Borda Count with parametrized exponential weighting."""

    weight = kwargs["weight"]
    candidates = {c.id: BordaCandidate(c.id) for c in candidates}
    vote_nr = 0
    for vote in votes:
        vote_nr += 1
        explain(
            f"                 \n======== Standings at vote {vote_nr} ========",
            do_explain,
        )
        for i, v_candidate in enumerate(vote.candidates):
            candidates[v_candidate].points += weight ** i
        for candidate in sorted(
            candidates.values(), key=lambda c: c.points, reverse=True
        ):
            explain(candidate, do_explain)

    return list(sorted(candidates.values(), key=lambda c: c.points, reverse=True))
