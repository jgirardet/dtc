import pathlib
import json

import pytest

from dtc import from_json

from dtc import cache


@pytest.fixture(scope="class")
def cache_clear_class(request):
    cache.clear()


@pytest.fixture(scope="function")
def cache_clear_function(request):
    cache.clear()


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
