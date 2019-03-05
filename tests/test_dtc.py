import json
import types
from dataclasses import asdict
from dataclasses import fields
from dataclasses import is_dataclass
from datetime import datetime

import pytest

from .samples import DDateTTime
from .samples import DTIME
from .samples import First_nested
from .samples import JSON_LIST
from .samples import JSON_LIST_INSIDE_OBJ
from .samples import JSON_LIST_INSIDE_OBJ_CUSTOM
from .samples import JsonListDataclass
from .samples import Obj
from .samples import One_object
from .samples import SAMPLE
from .samples import SampleDataClass
from .samples import Second_nested
from .samples import SimpleList
from .utils import cc
from .utils import compare_class
from .utils import compare_instance
from .utils import custom_fn
from .utils import get_field
from dtc import create_dataclass
from dtc import Custom
from dtc import from_dict
from dtc import from_json
from dtc import from_list
from dtc import populate

pytestmark = pytest.mark.usefixtures("cache_clear")


class TestCreateDataclass:
    def test_simple(self):
        dt = create_dataclass({"string": "bla"}, "Objj")
        assert is_dataclass(dt)
        assert compare_class(Obj, dt)

    def test_name_capswords(self):
        data = {"text": "bla'"}
        dt = create_dataclass(data, "obj")
        dt.__name__ == "Obj"

    def test_datetime(self):
        dt = create_dataclass(
            {"when": "2012-04-21T18:25:43-05:00"},
            "Dd",
            custom={"when": {"type": datetime}},
        )
        assert is_dataclass(dt)
        assert compare_class(DDateTTime, dt, without="metadata")

    def test_custom_metadata(self):
        dt = create_dataclass(
            {"when": "2012-04-21T18:25:43-05:00"},
            "Dd",
            custom={"when": {"type": datetime}},
        )
        assert fields(dt)[0].metadata == {
            "autodtc": Custom(type=datetime, fn=None, args=[], kwargs={})
        }

    def test_custom_3_levels(self):
        dt = create_dataclass(
            {"first_nested": {"second_nested": {"dtime": "1324-12-12"}}},
            "ONe",
            custom={"first_nested.second_nested.dtime": {"type": datetime}},
        )

        assert get_field(dt, "first_nested.second_nested.dtime").type == datetime
        assert get_field(dt, "first_nested.second_nested.dtime").metadata == {
            "autodtc": Custom(type=datetime, fn=None, args=[], kwargs={})
        }

    def test_nested(self):
        dt = create_dataclass({"second_nested": {"rien": "bla"}}, "Fn")
        assert is_dataclass(dt)
        compare_class(First_nested, dt)

        assert is_dataclass(fields(dt)[0].type)
        compare_class(Second_nested, fields(dt)[0].type)

    def test_3_nested(self):
        dt = create_dataclass(
            {
                "first_nested": {"second_nested": {"rien": "bla"}},
                "texte": "text",
                "datedate": "1234-12-01",
            },
            "ONe",
            custom={"datedate": {"type": datetime}},
        )
        assert is_dataclass(dt)
        compare_class(One_object, dt, "metadata")

        # 2 level
        level2 = get_field(dt, "first_nested")
        assert is_dataclass(level2)
        compare_class(First_nested, level2)

        # 3rd level
        level3 = get_field(dt, "first_nested.second_nested")
        assert is_dataclass(level3)
        compare_class(Second_nested, level3)

    def test_list(self):
        data = {"maliste": [1, 2, 3]}
        dt = create_dataclass(data, "UneListe")
        compare_class(SimpleList, dt)

    def test_order(self):
        data = {"maliste": [1, 2, 3], "string": "bla"}
        assert create_dataclass(data, "UneListe")
        # should pass if order ok

    def test_sample(self):
        data = json.loads(SAMPLE)
        dt = create_dataclass(
            data,
            "Sample",
            custom={
                "timedate": {"type": datetime},
                "one_object.datedate": {"type": datetime},
            },
        )
        assert is_dataclass(dt)
        compare_class(SampleDataClass, dt, without="metadata")
        assert get_field(dt, "one_object.datedate").metadata == types.MappingProxyType(
            {"autodtc": Custom(datetime)}
        )

    def test_write_cache(self, cache_clear):
        data = {"text": "bla'"}
        dt = create_dataclass(data, "obj")
        dv = create_dataclass(data, "objo")
        assert cache_clear == {"Obj": dt, "Objo": dv}

    def test_get_cache_present_in_create_dataclass(self):
        data = {"Obj": {"text": "bla'"}}
        dt = create_dataclass(data["Obj"], "Obj")
        ddt = create_dataclass(data["Obj"], "Obj")
        assert dt is ddt

    def test_get_cache_present_inside_process_dict(self):
        data = {"text": "bla'"}
        data2 = {"obj": {"text": "molpj"}}
        dt = create_dataclass(data, "Obj")
        dt2 = create_dataclass(data2, "Obj2")
        assert get_field(dt2, "obj") is dt


class TestProcessList:
    def test_process_list_keep_only_one(self):
        data = json.loads(JSON_LIST)
        dt = create_dataclass(data, "ref")
        assert len(dt) == 1

    def test_process_list_class_ok(self):
        data = json.loads(JSON_LIST)
        dt = create_dataclass(data, "ref", custom={"timedate": {"type": datetime}})

        compare_class(JsonListDataclass, dt[0], "metadata")
        assert get_field(dt[0], "timedate").metadata == types.MappingProxyType(
            {"autodtc": Custom(datetime)}
        )

    def test_process_list_list_of_obj(self, cache_clear):
        data = json.loads(JSON_LIST_INSIDE_OBJ)
        create_dataclass(data, "ref")
        assert "Ref" in cache_clear
        assert "Objecs_item" in cache_clear


class TestPopulate:
    @pytest.mark.parametrize(
        "data, name,  custom, out",
        [
            ({"string": "bla"}, "Obj", {}, {"string": "bla"}),
            ({"string": "bla"}, "obj", {}, {"string": "bla"}),
            (
                {"when": "2012-04-21T18:25:43-05:00"},
                "obj",
                {"when": {"type": datetime}},
                {"when": DTIME},
            ),
            ({"maliste": [1, 2, 3]}, "obj", {}, {"maliste": [1, 2, 3]}),
            ({"nested": {"rien": "bla"}}, "obj", {}, {"nested": {"rien": "bla"}}),
        ],
    )
    def test_populate(self, data, name, custom, out):
        create_dataclass(data, name, custom)
        populated = asdict(populate(data, name))
        assert out == populated

    def test_populate_nested(self):
        name = "obj"
        data = {"nested": {"rien": "bla"}}
        create_dataclass(data, name)
        populated = populate(data, name)
        cached = cc("Obj")(nested=cc("Nested")(**data["nested"]))
        assert cached == populated

    def test_populate_nested_3_level(self, cache_clear):
        name = "obj"
        data = {"first_nested": {"second_nested": {"dtime": "1324-12-12"}}}
        create_dataclass(data, name)
        populated = populate(data, name)
        cached = cc("Obj")(
            first_nested=cc("First_nested")(
                second_nested=cc("Second_nested")(**{"dtime": "1324-12-12"})
            )
        )
        assert cached == populated

    def test_populate_nested_3_level_custom(self, cache_clear):
        name = "obj"
        data = {"first_nested": {"second_nested": {"dtime": "1324-12-12"}}}
        create_dataclass(
            data, name, custom={"first_nested.second_nested.dtime": {"type": datetime}}
        )
        populated = populate(data, name)
        cached = cc("Obj")(
            first_nested=cc("First_nested")(
                second_nested=cc("Second_nested")(**{"dtime": datetime(1324, 12, 12)})
            )
        )
        assert cached == populated

    def test_sample(self):
        data = json.loads(SAMPLE)
        create_dataclass(
            data,
            "Sample",
            custom={
                "timedate": {"type": datetime},
                "one_object.datedate": {"type": datetime},
            },
        )
        populated = populate(data, "Sample")
        # data["timedate"] = DTIME
        cached = cc("Sample")(
            flooat=12.564,
            boolean=True,
            integer=12,
            array=[1, 2, 3, 4],
            string="bla",
            obj=cc("Obj")(string="rinen"),
            timedate=DTIME,
            one_object=cc("One_object")(
                first_nested=cc("First_nested")(
                    second_nested=cc("Second_nested")(rien="rienstr")
                ),
                texte="text",
                datedate=datetime(1234, 12, 1),
            ),
            null=None,
        )
        assert cached == populated

        # As dict let datetime object unchanged

        to_dict = asdict(populated)
        to_dict["one_object"]["datedate"] = to_dict["one_object"]["datedate"].strftime(
            "%Y-%m-%d"
        )
        to_dict["timedate"] = to_dict["timedate"].isoformat()
        assert to_dict == data

    def test_list_of_obj(self, cache_clear):
        data = json.loads(JSON_LIST_INSIDE_OBJ_CUSTOM)
        create_dataclass(data, "ref", custom={"objecs.timedate": {"type": datetime}})
        a = populate(data, "ref")
        ref = cc("Ref")
        objecs_item = cc("Objecs_item")
        compare_instance(a, ref(a=1, objecs=[objecs_item(timedate=DTIME)]))

    def test_custom_fn(self):
        data = {"timedate": "21 04 2012"}
        ref = create_dataclass(
            data,
            "Ref",
            custom={
                "timedate": {
                    "type": datetime,
                    "fn": datetime.strptime,
                    "args": ["%d %m %Y"],
                }
            },
        )

        a = populate(data, "ref")
        compare_instance(a, ref(timedate=datetime(2012, 4, 21)))

    @pytest.mark.parametrize(
        "res, custom",
        [
            ("bla", {"text": {"fn": custom_fn}}),
            ("blaabcd", {"text": {"fn": custom_fn, "args": ["a", "b", "c", "d"]}}),
            (
                "blaabcdab",
                {
                    "text": {
                        "fn": custom_fn,
                        "args": ["a", "b", "c", "d"],
                        "kwargs": {"a": "A", "b": "B"},
                    }
                },
            ),
        ],
    )
    def test_custom_fn(self, res, custom):
        data = {"text": "bla"}
        create_dataclass(data, "Obj", custom=custom)
        assert populate(data, "Obj").text == res


class TestPopulateFrom:
    def test_populate_list(self):
        data = json.loads(JSON_LIST)
        res = from_list(data, "ref")
        Ref = cc("Ref")
        Objece = cc("Objece")
        assert res == [
            Ref(
                ref="refs/heads/master",
                timedate="2012-04-21T18:25:43-05:00",
                objece=Objece(typ="commit"),
            ),
            Ref(
                ref="refs/heads/master",
                timedate="2012-04-21T18:25:43-05:00",
                objece=Objece(typ="commit"),
            ),
            Ref(
                ref="refs/heads/master",
                timedate="2012-04-21T18:25:43-05:00",
                objece=Objece(typ="commit"),
            ),
        ]

    def test_populate_from_dict(self):
        data = json.loads(SAMPLE)
        res = from_dict(
            data,
            "Sample",
            custom={
                "timedate": {"type": datetime},
                "one_object.datedate": {"type": datetime},
            },
        )
        assert res == cc("Sample")(
            flooat=12.564,
            boolean=True,
            integer=12,
            array=[1, 2, 3, 4],
            string="bla",
            obj=cc("Obj")(string="rinen"),
            timedate=DTIME,
            one_object=cc("One_object")(
                first_nested=cc("First_nested")(
                    second_nested=cc("Second_nested")(rien="rienstr")
                ),
                texte="text",
                datedate=datetime(1234, 12, 1),
            ),
            null=None,
        )

    @pytest.mark.parametrize(
        "param, fn",
        [([], from_dict), ({}, from_list), (b"1", from_json), (b'"a"', from_json)],
    )
    def test_bad_type(self, param, fn):
        with pytest.raises(TypeError):
            fn(param, "mock")


class TestCache:
    def test_instance(self):
        from dtc import cache

        assert cache == {}
        a = create_dataclass({}, "rien")
        assert cache == {"Rien": a}


# TODO
# REadme
# frontend
#
