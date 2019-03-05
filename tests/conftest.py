import pathlib
import json

import pytest

from dtc import from_json


@pytest.fixture(scope="function")
def cache(request):
    import dtc

    return dtc.cache

@pytest.fixture(scope="function")
def cache_clear(request):
    import dtc

    dtc.cache = {}

    return  dtc.cache


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