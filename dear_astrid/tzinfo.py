__all__ = [
  'UTC',
]

# from http://docs.python.org/2/library/datetime.html#tzinfo-objects

from datetime import tzinfo, timedelta, datetime

ZERO = timedelta(0)

# A UTC class.

class UTC(tzinfo):
  """UTC"""

  def utcoffset(self, dt):
    return ZERO

  def tzname(self, dt):
    return "UTC"

  def dst(self, dt):
    return ZERO
