import datetime

import dear_astrid.constants
from dear_astrid.constants import *

__all__ = [
  'dtu',
] + dear_astrid.constants.__all__

def dtu(*args):
  args = list(args)
  while len(args) < 7:
    args.append(0)
  return datetime.datetime(*(args + [dear_astrid.constants.UTC]))
