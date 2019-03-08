from dataclasses import field
from dataclasses import make_dataclass
from typing import Callable
from typing import Type


class Cache(dict):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = super().__new__(class_, *args, **kwargs)
        return class_._instance

    def __call__(self, val):
        return self[val]


cache = Cache()


Custom = make_dataclass(
    "Custom",
    [
        ["type", Type, field(default=None)],
        ["fn", Callable, field(default=None)],
        ["args", list, field(default_factory=list)],
        ["kwargs", dict, field(default_factory=dict)],
    ],
)
