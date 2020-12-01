import typing

from . import Candidate, Vote, explain


class BordaCandidate(Candidate):
    def __init__(self, id):
        self.id = id
        self._points = 0
        self.last_add = None

    def __str__(self):
        return f"{self.id}" f"\tpoints={self.points}\tlast_add={self.last_add}"

    @property
    def points(self):
        return self._points

    def add_points(self, points):
        self.last_add = points
        self._points += points


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
        points = max_points
        for c in candidates.values():
            c.last_add = 0
        for v_candidate in vote.candidates:
            candidates[v_candidate].add_points(points)
            points -= 1
            if points <= 0:
                break
        for candidate in sorted(
            candidates.values(), key=lambda c: c.points, reverse=True
        ):
            explain(candidate, do_explain)

    return list(sorted(candidates.values(), key=lambda c: c.points, reverse=True))
