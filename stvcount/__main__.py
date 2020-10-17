import sys
import typing


class Choice:
    def __init__(self, id):
        self.id = id
        self.num_votes = 0
        self.percentage = 0
        self.is_tied = False
        self.condorcet_score = 0

    def __repr__(self):
        return f"<Choice: {self.id} - {self.percentage}>"

    def __str__(self):
        return str(self.id) + (" (tied)" if self.is_tied else "")


class Vote:
    def __init__(self, choices):
        self.choices = choices

    def __repr__(self):
        return f"<Vote: {self.choices}>"


def condorcet(choice1: Choice, choice2: Choice, votes: typing.List[Vote]):
    pass


def stv(num_seats, choices: typing.List[Choice], votes: typing.List[Vote]):
    victory_quota = 1 / num_seats
    winners = []
    seats_filled = False
    # print(winners)
    # print(choices)
    # print(votes)
    while not seats_filled and votes:
        # Reset tallies
        for id, choice in choices.items():
            choice.num_votes = 0
            choice.percentage = 0

        # Count votes and calculate percentages
        for vote in votes:
            try:
                choice_id = vote.choices[0]
            except IndexError:
                raise RuntimeError(
                    "should never happen; no empty votes should exist here"
                )
            choices[choice_id].num_votes += 1
        for id, choice in choices.items():
            choice.percentage = choice.num_votes / len(votes)

        # print("                 ")
        # print(winners)
        # print(choices)
        # print(votes)

        # Find leader and last place
        leaders = []
        leader_pecentage = 0
        last_choice = None
        last_choice_percentage = 100
        for id, choice in choices.items():
            if choice.percentage > leader_pecentage:
                leader_pecentage = choice.percentage
                leaders = [choice]
            elif choice.percentage == leader_pecentage:
                leaders.append(choice)
            if choice.percentage < last_choice_percentage:
                last_choice_percentage = choice.percentage
                last_choice = choice

        # Is there a winner?
        if leaders and leader_pecentage >= victory_quota:
            # Yes
            tied_for_last_seats = len(winners) + len(leaders) > num_seats
            for leader in leaders:
                if tied_for_last_seats:
                    leader.is_tied = True
                winners.append(choices.pop(leader.id))
            if len(winners) >= num_seats:
                # All seats filled
                break
            for vote in votes:
                for leader in leaders:
                    if leader.id in vote.choices:
                        vote.choices.remove(leader.id)
        elif last_choice:
            # No, eliminate lowest scoring
            choices.pop(last_choice.id)
            for vote in votes:
                if last_choice.id in vote.choices:
                    vote.choices.remove(last_choice.id)
        else:
            raise RuntimeError("idk what to do now")

        # Remove empty votes
        votes = list(filter(lambda v: len(v.choices) > 0, votes))

    return winners


def main():
    num_seats = int(sys.argv[1])

    with open(sys.argv[2]) as input_file:
        input_rows = input_file.readlines()

    choices_row = input_rows.pop(0).split()
    votes_rows = [row.split() for row in input_rows]

    choices = {id: Choice(id) for id in choices_row}
    votes = [Vote(choices) for choices in votes_rows]

    for winner in stv(num_seats, choices, votes):
        print(winner)


if __name__ == "__main__":
    main()
