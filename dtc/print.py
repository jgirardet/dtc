from dataclasses import fields
from dataclasses import MISSING

import black

CLASS_PARAMS = {
    "init": True,
    "repr": True,
    "eq": True,
    "order": False,
    "unsafe_hash": False,
    "frozen": False,
}

FIELD_PARAMS = {"init": True, "repr": True, "hash": None, "compare": True}


def format_header(dc):
    f = dc.__dataclass_params__

    diff = diff_params(f, CLASS_PARAMS)

    # format params
    str_params = ", ".join(
        (f"{k}={v}" for k, v in diff.items() if v != CLASS_PARAMS[k])
    ).strip()
    str_params = "(" + str_params + ")" if str_params else ""

    # decorator line
    output = f"@dataclass" + str_params
    # classname line
    output += f"\nclass {dc.__class__.__name__}:\n"

    return output


def format_field(f):
    # base field
    output = f"{f.name}: {f.type.__name__}"

    # default params. string should quoted
    default = f.default if f.default != MISSING else None
    if isinstance(default, str):
        default = '"{}"'.format(default)
    # like default, default_factory is None if miissing
    default_factory = f.default_factory if f.default_factory != MISSING else None

    diff = diff_params(f, FIELD_PARAMS)
    if default_factory or diff:
        output += " = field("

        if default_factory:
            output += f"default_factory={f.default_factory.__name__},"

        elif default:
            output += f"default={default},"

        for k, v in diff.items():
            output += f"{k}={v},"
        output += ")"

    # do not creat diff if only defaut
    elif default:
        output += f" = {default}"

    return output + "\n"


def format_class(dt):
    res = format_header(dt)
    for i in fields(dt):
        res += f"\t{format_field(i)}"
    return black.format_str(res, black.DEFAULT_LINE_LENGTH)


def diff_params(obj, default):
    """ Return from obj, k/v if k in default but only if value differs"""
    params_f = {x: getattr(obj, x) for x in default}
    return {k: v for k, v in params_f.items() if v != default[k]}
