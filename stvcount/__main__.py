import sys


class Choice:
    def __init__(self, id):
        self.id = id
        self.num_votes = 0
        self.percentage = 0

    def __repr__(self):
        return f"<Choice: {self.id} - {self.percentage}>"


class Vote:
    def __init__(self, choices):
        self.choices = choices

    def __repr__(self):
        return f"<Vote: {self.choices}>"


def main():
    num_seats = int(sys.argv[1])

    with open(sys.argv[2]) as input_file:
        input_rows = input_file.readlines()

    choices_row = input_rows.pop(0).split()
    votes_rows = [row.split() for row in input_rows]

    choices = {id: Choice(id) for id in choices_row}
    votes = [Vote(choices) for choices in votes_rows]
    victory_treshold = 1 / num_seats
    # print(choices)
    # print(votes)

    winners = []
    seats_filled = False
    # print(winners)
    # print(choices)
    # print(votes)
    while not seats_filled and votes:
        # Count votes
        for vote in votes:
            try:
                choice_id = vote.choices[0]
            except IndexError:
                raise RuntimeError(
                    "should never happen; no empty votes should exist here"
                )
            choices[choice_id].num_votes += 1

        # Calculate percentages
        for id, choice in choices.items():
            choice.percentage = choice.num_votes / len(votes)

        print("                 ")
        print(winners)
        print(choices)
        print(votes)

        # Find leader and last place
        leading_choice = None
        leading_choice_percentage = 0
        last_choice = None
        last_choice_percentage = 100
        for id, choice in choices.items():
            if choice.percentage > leading_choice_percentage:
                leading_choice_percentage = choice.percentage
                leading_choice = choice
            if choice.percentage < last_choice_percentage:
                last_choice_percentage = choice.percentage
                last_choice = choice

        # Is there a winner?
        if leading_choice and leading_choice_percentage >= victory_treshold:
            # Yes, remove choice from all votes
            winners.append(choices.pop(leading_choice.id))
            if len(winners) >= num_seats:
                # All seats filled
                break
            for vote in votes:
                if leading_choice.id in vote.choices:
                    vote.choices.remove(leading_choice.id)
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

        # Reset tallies
        for id, choice in choices.items():
            choice.num_votes = 0
            choice.percentage = 0

    for winner in winners:
        print(winner.id)


if __name__ == "__main__":
    main()
