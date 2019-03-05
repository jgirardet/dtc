from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta

SAMPLE = b"""{
   "flooat": 12.564,
   "boolean": true,
   "integer": 12,
   "array": [1,2,3,4],
   "string": "bla",
   "obj": {"string":"rinen"},
   "timedate": "2012-04-21T18:25:43-05:00",
   "one_object": {
        "first_nested":{"second_nested":{"rien":"rienstr"}},
        "texte":"text",
        "datedate": "1234-12-01"
   },
   "null": null
   }"""


DTIME = datetime(
    2012, 4, 21, 18, 25, 43, tzinfo=timezone(timedelta(days=-1, seconds=68400))
)


@dataclass
class DDateTTime:
    when: datetime


@dataclass
class Second_nested:
    rien: str


@dataclass
class First_nested:
    second_nested: Second_nested


@dataclass
class One_object:
    first_nested: First_nested
    texte: str
    datedate: datetime


@dataclass
class Obj:
    string: str


@dataclass
class SampleDataClass:
    flooat: float
    boolean: bool
    integer: int
    string: str
    obj: Obj
    timedate: datetime
    one_object: One_object
    null: type(None)
    array: list = field(default_factory=list)


@dataclass
class SimpleList:
    maliste: list = field(default_factory=list)


@dataclass
class Objec:
    typ: str


@dataclass
class Objece:
    typ: str


@dataclass
class JsonListDataclass:
    ref: str
    timedate: datetime
    objece: Objece


JSON_LIST = b"""[
  {
    "ref": "refs/heads/master",
    "timedate": "2012-04-21T18:25:43-05:00",
    "objece": {
      "typ": "commit"
    }
  },
  {
    "ref": "refs/heads/master",
    "timedate": "2012-04-21T18:25:43-05:00",
    "objece": {
      "typ": "commit"
    }
  },
  {
    "ref": "refs/heads/master",
    "timedate": "2012-04-21T18:25:43-05:00",
    "objece": {
      "typ": "commit"
    }
  }
]"""


JSON_LIST_INSIDE_OBJ = b"""{
"a":1,
"objecs": [{"typ":"bla"},{"typ":"bla"},{"typ":"bla"}]}"""


JSON_LIST_INSIDE_OBJ_CUSTOM = b"""{
"a":1,
"objecs": [{"timedate": "2012-04-21T18:25:43-05:00"}]}"""
