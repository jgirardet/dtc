import json
import pathlib
from dataclasses import asdict

import pytest

from dtc import cache
from dtc import from_json
from dtc.compat import datetime



@pytest.mark.usefixtures("cache_clear_class", "big")
class TestBigStandard:
    def test_cache(self):
        assert set(cache.keys()) == set("Ref Name Friends_item".split())

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


class TestBigCustom:
    def test_datetime_fn(self, cache_clear_function):
        pp = pathlib.Path(__file__).parent / "big.json"
        dt = from_json(
            pp.read_text(),
            "ref",
            custom={
                "registered": {
                    "type": datetime,
                    "fn": datetime.strptime,
                    "args": ["%A, %B %d, %Y %I:%M %p"],
                }
            },
        )
        # assert False
        assert [x.registered for x in dt] == [
            datetime.strptime(y["registered"], "%A, %B %d, %Y %I:%M %p")
            for y in json.loads(pp.read_text())
        ]
