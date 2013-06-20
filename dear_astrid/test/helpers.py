import datetime
import os
import sys
import time

from dear_astrid.constants import *
from dear_astrid.constants import __all__ as _constants_all
from dear_astrid.tzinfo import *
from dear_astrid.tzinfo import __all__ as _tzinfo_all

__all__ = [
  'dtu',
  'u',
  'timezone',
] + _constants_all + _tzinfo_all


def dtu(*args):
  args = list(args)
  while len(args) < 7:
    args.append(0)
  return datetime.datetime(*(args + [UTC()]))

class timezone(object):
  def __init__(self, tz=None):
    self.tz = tz
    self.orig = None

  def set_env(self, tz):
    if tz is None:
      if 'TZ' in os.environ:
        del os.environ['TZ']
    else:
      os.environ['TZ'] = tz
    time.tzset()

  def __enter__(self):
    self.orig = os.environ.get('TZ', None)
    self.set_env(self.tz)

  def __exit__(self, *args):
    self.set_env(self.orig)

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
