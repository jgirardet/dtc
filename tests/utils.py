from itertools import zip_longest
from dataclasses import fields, is_dataclass, Field


def compare_class(dt1, dt2, without=set(), verbose=False):
    if isinstance(without, str):
        without = {without}
    for o, t in zip_longest(fields(dt1), fields(dt2)):
        compare_field(o, t, without, verbose)
    return True


def compare_field(one, two, without=set(), verbose=False):
    attrs = {
        "name",
        "type",
        "default",
        "default_factory",
        "init",
        "repr",
        "hash",
        "compare",
        "metadata",
        "_field_type",
    }
    if without - attrs:
        raise ValueError("without should be on of {}".format(attrs))
    attrs = attrs - without

    for attr in attrs:
        o = getattr(one, attr)
        t = getattr(two, attr)

        try:
            if (
                attr == "type"
                and o is not None
                and o.__module__.startswith("tests.samples")
            ):
                assert o.__name__ == t.__name__
            else:
                assert o == t
        except AssertionError as err:
            loc = {k: v for k, v in locals().items() if not k.startswith("@py_")}

            for k, v in loc.items():
                print(k, " = ", v)
            raise err

    if without and verbose:
        print("skipped : ", without)


def get_one_field(key, dtc, stop=False):
    for fs in fields(dtc):
        if fs.name == key:
            if is_dataclass(fs.type):
                return fs.type
            else:
                return fs


def get_field(dtc, field):
    tree = field.split(".")
    pinned = dtc

    for key in tree:
        if isinstance(Field, pinned):
            return pinned
        pinned = get_one_field(key, pinned)
    return pinned


def compare_instance(one, two):
    f_one = {f.name for f in fields(one)}
    f_two = {f.name for f in fields(two)}
    fs = f_one | f_two
    for f in fs:
        o = getattr(one, f)
        t = getattr(two, f)
        try:
            assert o == t
        except AssertionError as err:
            loc = {k: v for k, v in locals().items() if not k.startswith("@py_")}

            for k, v in loc.items():
                print(k, " = ", v)
            raise err


def custom_fn(x, *args, **kwargs):
    return x + "".join(args) + "".join(kwargs)


def cc(name):
    import dtc

    return dtc.cache[name]
