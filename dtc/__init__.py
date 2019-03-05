import json
from collections import namedtuple
from dataclasses import field
from dataclasses import fields
from dataclasses import make_dataclass
from dataclasses import MISSING
from datetime import datetime
from string import capwords
from typing import List
from typing import Union

ITEM = "_item"
BASE_NAME = "Base"

Custom = namedtuple(
    "Custom", ["type", "fn", "args", "kwargs"], defaults=[None, None, [], {}]
)

cache = {}


def create_dataclass(datas: Union[dict, list], name: str, custom: dict = {}):

    name = capwords(name)
    # Reuse cached already created class
    if name in cache:
        return cache[name]

    if isinstance(datas, dict):
        return process_dict(datas, name, custom)

    elif isinstance(datas, list):
        return process_list(datas, name, custom)


def process_list(datas, name, custom):
    new_classes = []
    for p in datas:
        new_dt = create_dataclass(p, name, custom)
        if new_dt not in new_classes:
            new_classes.append(new_dt)

    return new_classes


def _do_dict(key, value, custom):
    _key = capwords(key)
    if _key in cache:
        k_type = cache[_key]
    else:
        k_type = create_dataclass(
            datas=value, name=key, custom=reduce_custom(key, custom)
        )
    return k_type


def _do_list(key, value, custom):
    if isinstance(value[0], dict):
        k_type = List[
            create_dataclass(value[0], key + ITEM, reduce_custom(key, custom))
        ]
    else:
        k_type = list
    k_field = field(default_factory=list, default=MISSING)
    return k_type, k_field


def _do_custom(key, custom):
    custom_params = Custom(**custom[key])
    k_type = custom_params.type
    k_field = field(default=MISSING, metadata={"autodtc": custom_params})
    return k_type, k_field


def reduce_custom(key, custom):
    return {
        k.replace(key + ".", ""): v
        for k, v in custom.items()
        if k.startswith(key + ".")
    }


def process_dict(datas, name, custom):

    attibutes = []
    with_defaults_attributes = []

    # iterate over the dict
    for key, value in datas.items():
        k_type = None
        k_field = field(default=MISSING)

        # custom params overide everything else
        if key in custom:
            k_type, k_field = _do_custom(key, custom)

        # list should be handled as default_factory
        if isinstance(value, list):
            k_type, k_field = _do_list(key, value, custom)

        # create subobjects
        elif isinstance(value, dict):
            k_type = _do_dict(key, value, custom)

        # handle null type
        elif value is None:
            k_type = type(None)

        # standard value
        else:
            k_type = k_type or type(value)

        # no default have to be first
        if k_field.default != MISSING or k_field.default_factory != MISSING:
            with_defaults_attributes.append([key, k_type, k_field])
        else:
            attibutes.append([key, k_type, k_field])

    # write cache
    cache[name] = make_dataclass(name, attibutes + with_defaults_attributes)

    return cache[name]


def populate(datas, class_name):
    "takes class_name, returns  datas returns instance"

    current_class = create_dataclass(datas, class_name)
    new_data = {}
    for f in fields(current_class):
        key = f.name
        value = datas[key]
        custom = f.metadata.get("autodtc", {})

        if getattr(custom, "fn", None):
            new_data[key] = custom.fn(value, *custom.args, **custom.kwargs)
        elif f.type is datetime:
            new_data[key] = datetime.fromisoformat(value)

        elif isinstance(value, dict):
            new_data[key] = populate(value, key)
        elif isinstance(value, list):
            if isinstance(value[0], dict):
                new_data[key] = [populate(item, key + ITEM) for item in value]
            else:
                new_data[key] = value

        else:
            new_data[key] = value

    return current_class(**new_data)


def from_list(datas, class_name=BASE_NAME, custom={}):
    "parse list"
    if not isinstance(datas, (list, tuple)):
        raise TypeError("input datas should be a list or a tuple")
    entities = []
    create_dataclass(datas, class_name, custom)
    for item in datas:
        entities.append(populate(item, class_name))
    return entities


def from_dict(datas, class_name=BASE_NAME, custom={}):
    if not isinstance(datas, dict):
        raise TypeError("input datas should be a dict")
    create_dataclass(datas, class_name, custom)
    return populate(datas, class_name)


def from_json(datas, class_name=BASE_NAME, custom={}, parser=json, *args, **kwargs):
    loaded = parser.loads(datas, *args, **kwargs)
    from_fn = None
    if isinstance(loaded, list):
        from_fn = from_list
    elif isinstance(loaded, dict):
        from_fn = from_dict

    else:
        raise TypeError("input datas should be a javascript's object or array ")

    return from_fn(loaded, class_name, custom)
