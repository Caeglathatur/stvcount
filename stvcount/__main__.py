import sys
import typing
from copy import deepcopy


class Candidate:
    def __init__(self, id):
        self.id = id
        self.num_votes = 0
        self.percentage = 0
        self.is_tied = False
        self.condorcet_score = 0

    def __repr__(self):
        return f"<Candidate: {self.id} - {self.percentage} - {self.condorcet_score}>"

    def __str__(self):
        return str(self.id) + (" (tied)" if self.is_tied else "")


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
        candidate.percentage = 0

    # Count votes and calculate percentages
    for vote in votes:
        try:
            candidate_id = vote.candidates[0]
        except IndexError:
            raise RuntimeError("should never happen; no empty votes should exist here")
        candidates[candidate_id].num_votes += 1

    if candidate1.num_votes > candidate2.num_votes:
        candidate1.condorcet_score += 1
    elif candidate2.num_votes > candidate1.num_votes:
        candidate2.condorcet_score += 1


def condorcet(candidates: typing.List[Candidate], votes: typing.List[Vote]):
    for i, candidate1 in enumerate(candidates):
        for j in range(i + 1, len(candidates)):
            candidate2 = candidates[j]
            condorcet_pair(candidate1, candidate2, deepcopy(votes))


def find_lowest_condorcet(candidates: typing.List[Candidate]):
    return (
        sorted(candidates, key=lambda c: c.condorcet_score)[0] if candidates else None
    )


def stv(num_seats, candidates: typing.Dict[id, Candidate], votes: typing.List[Vote]):
    victory_quota = 1 / num_seats
    winners = []

    condorcet(list(candidates.values()), deepcopy(votes))

    # print(winners)
    # print(candidates)
    # print(votes)

    while votes:
        # Reset tallies
        for candidate in candidates.values():
            candidate.num_votes = 0
            candidate.percentage = 0

        # Count votes and calculate percentages
        for vote in votes:
            try:
                candidate_id = vote.candidates[0]
            except IndexError:
                raise RuntimeError(
                    "should never happen; no empty votes should exist here"
                )
            candidates[candidate_id].num_votes += 1
        for candidate in candidates.values():
            candidate.percentage = candidate.num_votes / len(votes)

        # print("                 ")
        # print(winners)
        # print(candidates)
        # print(votes)

        # Find leader and last place
        leaders = []
        leader_pecentage = 0
        for candidate in candidates.values():
            if candidate.percentage > leader_pecentage:
                leader_pecentage = candidate.percentage
                leaders = [candidate]
            elif candidate.percentage == leader_pecentage:
                leaders.append(candidate)

        # Is there a winner?
        if leaders and leader_pecentage >= victory_quota:
            # Yes
            # Remove excess winners based on condorcet score
            num_tied_for_last = len(winners) + len(leaders) - num_seats
            if num_tied_for_last > 0:
                for i in range(num_tied_for_last):
                    leaders.remove(find_lowest_condorcet(leaders))
            for leader in leaders:
                winners.append(candidates.pop(leader.id))
            if len(winners) >= num_seats:
                # All seats filled
                break
            # Remove winners from votes
            for vote in votes:
                for leader in leaders:
                    if leader.id in vote.candidates:
                        vote.candidates.remove(leader.id)
        else:
            # No, eliminate candidate with lowest condorcet score
            last_candidate = find_lowest_condorcet(candidates.values())
            candidates.pop(last_candidate.id)
            # Remove excluded from votes
            for vote in votes:
                if last_candidate.id in vote.candidates:
                    vote.candidates.remove(last_candidate.id)

        # Remove empty votes
        votes = list(filter(lambda v: len(v.candidates) > 0, votes))

    return winners


def main():
    num_seats = int(sys.argv[1])

    with open(sys.argv[2]) as input_file:
        input_rows = input_file.readlines()

    candidates_row = input_rows.pop(0).split()
    votes_rows = [row.split() for row in input_rows]

    candidates = {id: Candidate(id) for id in candidates_row}
    votes = [Vote(candidates) for candidates in votes_rows]

    for winner in stv(num_seats, candidates, votes):
        print(winner)


if __name__ == "__main__":
    main()
