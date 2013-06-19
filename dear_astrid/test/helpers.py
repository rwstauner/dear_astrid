import datetime
import sys

from dear_astrid.constants import *
from dear_astrid.constants import __all__ as _constants_all
from dear_astrid.tzinfo import *
from dear_astrid.tzinfo import __all__ as _tzinfo_all

__all__ = [
  'dtu',
  'u',
] + _constants_all + _tzinfo_all


def dtu(*args):
  args = list(args)
  while len(args) < 7:
    args.append(0)
  return datetime.datetime(*(args + [UTC()]))

PY3 = False
try:
  PY3 = (sys.version_info.major == 3)
except:
  pass

if PY3:
  def u(string):
    return string
else:
  exec("def u(string):\n  return string + u''\n")
