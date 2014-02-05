import datetime
import os
import re
import time
import unittest

# pylint: disable=wildcard-import,invalid-name

from dear_astrid.constants import *
from dear_astrid.constants import __all__ as _constants_all
from dear_astrid.tzinfo import *
from dear_astrid.tzinfo import __all__ as _tzinfo_all

__all__ = [
  'dtu',
  'timezone',
  'TestCase',
] + _constants_all + _tzinfo_all


def dtu(*args):
  """Return datetime object in UTC."""
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

class TestCase(unittest.TestCase):
  def __init__(self, *args, **kwargs):
    super(TestCase, self).__init__(*args, **kwargs)
    # unittest2
    self.longMessage = True
    self.maxDiff     = 80*20

finder = re.compile(r'^assert[A-Z]')
renamer = re.compile('([a-z])([A-Z])')
underscore = lambda m: '_'.join([m.group(1), m.group(2).lower()])
# pylint: disable=bad-builtin
for meth in filter(finder.match, unittest.TestCase.__dict__.keys()):
  under = renamer.sub(underscore, meth)
  setattr(TestCase, under, getattr(unittest.TestCase, meth))
