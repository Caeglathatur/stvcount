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


def borda_even(
    num_seats,
    candidates: typing.List[Candidate],
    votes: typing.List[Vote],
    do_explain=False,
    **kwargs,
) -> typing.List[Candidate]:
    """Borda Count, but for each vote, divide unassigned points evenly among
    all omitted candidates. Each vote is thus worth an equal number of points.
    """

    max_points = kwargs.get("max_per_vote", None) or len(candidates)
    candidates = {c.id: BordaCandidate(c.id) for c in candidates}
    vote_nr = 0
    for vote in votes:
        vote_nr += 1
        vote_total_points = 0
        explain(
            f"                 \n======== Standings at vote {vote_nr} ========",
            do_explain,
        )
        points = max_points
        for v_candidate in vote.candidates:
            candidates[v_candidate].add_points(points)
            vote_total_points += points
            points -= 1
            if points <= 0:
                break
        remaining = [c for c in candidates.values() if c.id not in vote.candidates]
        each = (1 + len(remaining)) / 2
        for candidate in remaining:
            candidate.add_points(each)
            vote_total_points += each
        explain(f"Total points assigned in vote: {vote_total_points}", do_explain)
        for candidate in sorted(
            candidates.values(), key=lambda c: c.points, reverse=True
        ):
            explain(candidate, do_explain)

    return list(sorted(candidates.values(), key=lambda c: c.points, reverse=True))
