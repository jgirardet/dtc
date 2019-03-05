import json
import pathlib
from dataclasses import asdict
from datetime import datetime

import pytest

from dtc import from_json

pytestmark = pytest.mark.usefixtures("ch", "big", "big_c")


@pytest.fixture(scope="class")
def ch(request):
    import dtc

    dtc.cache = {}
    yield dtc.cache


def parse_big(custom={}):
    path = pathlib.Path(__file__).parent / "big.json"
    return from_json(open(path).read(), "ref", custom=custom)


@pytest.fixture(scope="class")
def big(request):
    return parse_big()


@pytest.fixture(scope="class")
def big_j(request):
    path = pathlib.Path(__file__).parent / "big.json"
    return json.loads(open(path).read())


@pytest.mark.usefixtures('ch')
class TestBigStandard:
    def test_cache(self, ch):
        assert set(ch.keys()) == set("Ref Name Friends_item".split())

    def test_len(self, big):
        len(big) == 5

    @pytest.mark.parametrize(
        "param", "_id index guid isActive balance picture age eyeColor tags".split()
    )
    def test_simple_fields_and_list(self, big, big_j, param):
        assert [getattr(x, param) for x in big] == [x[param] for x in big_j]

    @pytest.mark.parametrize("param", "name".split())
    def test_obejct_fields(self, big, big_j, param):
        assert [asdict(getattr(x, param)) for x in big] == [x[param] for x in big_j]

    @pytest.mark.parametrize("param", "friends".split())
    def test_dict_in_list_fields(self, big, big_j, param):
        assert [asdict(y) for x in big for y in getattr(x, param)] == [
            y for x in big_j for y in x[param]
        ]


@pytest.fixture(scope="class")
def big_c(request):
    return parse_big(
        custom={
            "registered": {
                "type": datetime,
                "fn": datetime.strptime,
                "args": ["%A, %B %d, %Y %I:%M %p"],
            }
        }
    )

@pytest.mark.usefixtures('ch', 'big_c')
class TestBigCustom:
    @pytest.mark.parametrize("param", "registered".split())
    def test_datetime_fn(self, big_c, big_j, param, ch):
        assert [getattr(x, param) for x in big_c] == [datetime.strptime(x[param], "%A, %B %d, %Y %I:%M %p")  for x in big_j]
