import unittest
from copy import deepcopy

from . import Candidate, Vote
from .stv import stv


class STVTest(unittest.TestCase):
    def test_0(self):
        num_seats = 1
        winners = stv(
            num_seats=num_seats,
            candidates=[
                Candidate("0"),
                Candidate("1"),
            ],
            votes=[
                Vote(["0"]),
                Vote(["1"]),
                Vote(["1"]),
            ],
        )
        self.assertEqual(len(winners), num_seats)
        self.assertEqual(winners[0].id, "1")

    def test_1(self):
        num_seats = 1
        winners = stv(
            num_seats=num_seats,
            candidates=[
                Candidate("0"),
                Candidate("1"),
                Candidate("2"),
            ],
            votes=[
                Vote(["0"]),
                Vote(["1", "0"]),
                Vote(["2"]),
            ],
        )
        self.assertEqual(len(winners), num_seats)
        self.assertEqual(winners[0].id, "0")

    def test_2(self):
        num_seats = 1
        winners = stv(
            num_seats=num_seats,
            candidates=[
                Candidate("0"),
                Candidate("1"),
                Candidate("2"),
            ],
            votes=[
                Vote(["0", "2", "1"]),
                Vote(["1", "0", "2"]),
                Vote(["2", "0", "1"]),
            ],
        )
        self.assertEqual(len(winners), num_seats)
        self.assertEqual(winners[0].id, "0")

    def test_3(self):
        num_seats = 1
        winners = stv(
            num_seats=num_seats,
            candidates=[
                Candidate("0"),
                Candidate("1"),
                Candidate("2"),
            ],
            votes=[
                Vote(["0", "2", "1"]),
                Vote(["0", "2", "1"]),
                Vote(["2", "0", "1"]),
            ],
        )
        self.assertEqual(len(winners), num_seats)
        self.assertEqual(winners[0].id, "0")

    def test_4(self):
        num_seats = 2
        winners = stv(
            num_seats=num_seats,
            candidates=[
                Candidate("0"),
                Candidate("1"),
                Candidate("2"),
                Candidate("3"),
                Candidate("4"),
            ],
            votes=[
                Vote(["0", "2", "1"]),
                Vote(["0", "2", "1"]),
                Vote(["2", "0", "1"]),
            ],
        )
        self.assertEqual(len(winners), num_seats)
        self.assertEqual(winners[0].id, "0")
        self.assertEqual(winners[1].id, "2")

    def test_5(self):
        num_seats = 3
        winners = stv(
            num_seats=num_seats,
            candidates=[
                Candidate("0"),
                Candidate("1"),
                Candidate("2"),
                Candidate("3"),
                Candidate("4"),
            ],
            votes=[
                Vote(["0", "2", "1"]),
                Vote(["0", "2", "1"]),
                Vote(["2", "0", "1"]),
            ],
        )
        self.assertEqual(len(winners), num_seats)
        self.assertEqual(winners[0].id, "0")
        self.assertEqual(winners[1].id, "2")
        self.assertEqual(winners[2].id, "1")

    def test_6(self):
        num_seats = 3
        winners = stv(
            num_seats=num_seats,
            candidates=[
                Candidate("0"),
                Candidate("1"),
                Candidate("2"),
                Candidate("3"),
                Candidate("4"),
            ],
            votes=[
                Vote(["2", "1", "0"]),
                Vote(["1", "0", "2"]),
                Vote(["0", "2", "1"]),
            ],
        )
        self.assertEqual(len(winners), num_seats)
        for winner in winners:
            self.assertTrue(winner.id in ["0", "1", "2"])

    def test_7(self):
        num_seats = 3
        winners = stv(
            num_seats=num_seats,
            candidates=[
                Candidate("0"),
                Candidate("1"),
                Candidate("2"),
                Candidate("3"),
                Candidate("4"),
            ],
            votes=[
                Vote(["2", "1", "0"]),
                Vote(["1", "0", "2"]),
                Vote(["0", "2", "1"]),
                Vote(["3"]),
            ],
        )
        self.assertEqual(len(winners), num_seats)
        for winner in winners:
            self.assertTrue(winner.id in ["0", "1", "2"])

    def test_8(self):
        num_seats = 3
        winners = stv(
            num_seats=num_seats,
            candidates=[
                Candidate("0"),
                Candidate("1"),
                Candidate("2"),
                Candidate("3"),
                Candidate("4"),
            ],
            votes=[
                Vote(["2", "1", "0"]),
                Vote(["1", "0", "2"]),
                Vote(["0", "2", "1"]),
                Vote(["3", "2"]),
            ],
        )
        self.assertEqual(len(winners), num_seats)
        self.assertEqual(winners[0].id, "2")
        for winner in winners:
            self.assertTrue(winner.id in ["0", "1", "2"])

    def test_complex_with_tiebreaking(self):
        """The purpose of this test is not to validate behavior per-se, but to detect
        changed behavior. The scenario is known to make use of both the primary and
        secondary elimination tiebreakers for different values of num_seats.
        """

        candidates = [
            Candidate("1"),
            Candidate("2"),
            Candidate("3"),
            Candidate("4"),
            Candidate("5"),
            Candidate("6"),
            Candidate("7"),
            Candidate("8"),
            Candidate("9"),
            Candidate("10"),
            Candidate("11"),
            Candidate("12"),
            Candidate("13"),
            Candidate("14"),
            Candidate("15"),
            Candidate("16"),
            Candidate("17"),
            Candidate("18"),
            Candidate("19"),
            Candidate("20"),
            Candidate("21"),
        ]
        votes = [
            Vote(["13", "7", "2", "9", "14", "12", "1", "10", "15", "20"]),
            Vote(["14", "13", "17", "2", "9", "21", "1", "15", "12", "11"]),
            Vote(["9", "10", "20", "17", "2", "18", "3", "7", "13", "19"]),
            Vote(["14", "5", "7", "12", "21", "8", "11", "1", "20", "13"]),
            Vote(["18", "10", "11", "12", "2", "9", "14", "15", "6"]),
            Vote(["21", "7", "8", "3", "1", "13", "14"]),
            Vote(["17", "2", "19", "12", "5"]),
            Vote(["12", "9", "18", "17", "4", "1", "15", "11"]),
        ]

        for num_seats, expected_winners in [
            (1, ["12"]),
            (2, ["12", "13"]),
            # Interestingly, 13, which was second above, is not among the winners here
            (3, ["12", "9", "14"]),
            # And here 12, first winner of all previous cases, is not among the winners
            # at all. 13 is back, though.
            (4, ["14", "13", "17", "2"]),
            (5, ["14", "13", "17", "2", "9"]),
            (6, ["14", "13", "17", "2", "9", "21"]),
            (7, ["14", "13", "17", "2", "9", "21", "7"]),
            (8, ["14", "9", "12", "13", "17", "18", "21", "2"]),
            (9, ["14", "9", "12", "13", "17", "18", "21", "2", "7"]),
            (10, ["14", "9", "12", "13", "17", "18", "21", "2", "7", "10"]),
            (11, ["14", "9", "12", "13", "17", "18", "21", "2", "7", "10", "5"]),
            (12, ["14", "9", "12", "13", "17", "18", "21", "2", "7", "10", "5", "4"]),
        ]:
            with self.subTest(num_seats=num_seats):
                winners = stv(
                    num_seats=num_seats,
                    candidates=deepcopy(candidates),
                    votes=deepcopy(votes),
                )
                self.assertEqual(len(winners), num_seats)
                self.assertEqual([w.id for w in winners], expected_winners)


if __name__ == "__main__":
    unittest.main()
