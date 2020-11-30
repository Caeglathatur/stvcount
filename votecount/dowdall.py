import typing

from . import Candidate, Vote, explain


class DowdallCandidate(Candidate):
    def __init__(self, id):
        self.id = id
        self.points = 0

    def __str__(self):
        return f"{self.id}" f"\tpoints={self.points}"


def dowdall(
    num_seats,
    candidates: typing.List[Candidate],
    votes: typing.List[Vote],
    do_explain=False,
    **kwargs,
) -> typing.List[Candidate]:
    """Dowdall Count (Borda with a more pluralistic weighting of preferences)"""

    candidates = {c.id: DowdallCandidate(c.id) for c in candidates}
    vote_nr = 0
    for vote in votes:
        vote_nr += 1
        explain(
            f"                 \n======== Standings at vote {vote_nr} ========",
            do_explain,
        )
        for i, v_candidate in enumerate(vote.candidates):
            candidates[v_candidate].points += 1 / (i + 1)
        for candidate in sorted(
            candidates.values(), key=lambda c: c.points, reverse=True
        ):
            explain(candidate, do_explain)

    return list(sorted(candidates.values(), key=lambda c: c.points, reverse=True))
