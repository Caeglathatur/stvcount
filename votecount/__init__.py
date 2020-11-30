import typing


def explain(string, do_explain):
    if do_explain:
        print(string)


class Candidate:
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return f"<Candidate: {self.id}>"

    def __str__(self):
        return str(self.id)


class Vote:
    def __init__(self, candidates: typing.List[str]):
        seen = set()
        self.candidates: typing.List[str] = []
        for c in candidates:
            if c in seen:
                raise RuntimeError(
                    f'Found vote in which "{c}" appears more than once: '
                    f"{' '.join(candidates)}"
                )
            seen.add(c)
            self.candidates.append(c)

    def __repr__(self):
        return f"<Vote: {self.candidates}>"
