import datetime
import sys

import dear_astrid.constants
from dear_astrid.constants import *

__all__ = [
  'dtu',
  'u',
] + dear_astrid.constants.__all__

def dtu(*args):
  args = list(args)
  while len(args) < 7:
    args.append(0)
  return datetime.datetime(*(args + [dear_astrid.constants.UTC]))

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
