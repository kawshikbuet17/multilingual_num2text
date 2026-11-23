"""The small set of words every language must provide for the shared rules."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Words:
    digits: tuple[str, ...]
    negative: str
    decimal_point: str
    percent: str
    range: str
    slash: str
    ratio: str
    dot: str
    at: str
    star: str
    hash: str
    plus: str
    money_joiner: str = ""
    add: str = ""
    times: str = ""
    divided_by: str = ""
    equals: str = ""
    more_than: str = ""

    @property
    def symbols(self) -> dict[str, str]:
        return {"*": self.star, "#": self.hash, "+": self.plus}
