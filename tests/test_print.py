from dataclasses import dataclass
from dataclasses import field
from dataclasses import make_dataclass
from datetime import datetime

import black
import pytest

from dtc.print import format_class
from dtc.print import format_header


@pytest.mark.parametrize(
    "init_params, res",
    [
        ({"init": False}, "(init=False)"),
        ({}, ""),
        (
            {
                "init": False,
                "repr": False,
                # "eq": False,
                "order": True,
                "unsafe_hash": True,
                "frozen": True,
            },
            "(init=False, repr=False, order=True, unsafe_hash=True, frozen=True)",
        ),
        (
            {
                "init": False,
                "repr": False,
                "eq": False,
                # "order": True,
                "unsafe_hash": True,
                "frozen": True,
            },
            "(init=False, repr=False, eq=False, unsafe_hash=True, frozen=True)",
        ),
    ],
)
def test_headers(init_params, res):
    d = make_dataclass("", [], **init_params)
    res = "@dataclass" + res + "\nclass type:\n"
    assert format_header(d) == res


@dataclass
class E:
    boumboum: str
    boum: int = 5


@dataclass
class A:
    dd: datetime
    bla: int
    ble: str
    blo: int = field(repr=False)
    e: E
    blaf: int = 1
    blef: str = "mokmokff zef"
    bli: list = field(default_factory=list)
    blif: list = field(default_factory=list, repr=False)
    blof: int = field(repr=False, default=1)
    blouf: int = field(repr=False, default=1, hash=1, compare=False, init=False)


STR_A = black.format_str(
    """@dataclass
class A:
    dd: datetime
    bla: int
    ble: str
    blo: int = field(repr=False)
    e: E
    blaf: int = 1
    blef: str = "mokmokff zef"
    bli: list = field(default_factory=list)
    blif: list = field(default_factory=list, repr=False)
    blof: int = field(default=1, repr=False)
    blouf: int = field(default=1, init=False, repr=False, hash=1, compare=False)
""",
    black.DEFAULT_LINE_LENGTH,
)


e = E("bla")
a = A(dd=datetime(1320, 12, 1, 14, 20), bla=1, ble="mok", blo=3, e=e)


def test_print():
    assert STR_A == format_class(a)
