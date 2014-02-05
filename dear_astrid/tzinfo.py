"""
Tzinfo classes for UTC and local time.
"""

# pylint: disable=missing-docstring,unused-argument,invalid-name
# pylint: disable=no-self-use,super-init-not-called

__all__ = [
  'UTC',
  'LocalTimezone'
]

# from http://docs.python.org/2/library/datetime.html#tzinfo-objects

from datetime import tzinfo, timedelta

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

  # Make the test diffs smaller (by not printing the memory address).
  def __repr__(self):
    return str(type(self))

# A class capturing the platform's idea of local time.

import time as _time

class LocalTimezone(tzinfo):

  # Instead of setting these vars globally, reset them at every instantiation
  # so that changes to the time zone are reflected (useful for testing).
  def __init__(self):
    self.__STDOFFSET = timedelta(seconds = -_time.timezone)

    if _time.daylight:
      self.__DSTOFFSET = timedelta(seconds = -_time.altzone)
    else:
      self.__DSTOFFSET = self.__STDOFFSET

    self.__DSTDIFF = self.__DSTOFFSET - self.__STDOFFSET


  def utcoffset(self, dt):
    if self._isdst(dt):
      return self.__DSTOFFSET
    else:
      return self.__STDOFFSET

  def dst(self, dt):
    if self._isdst(dt):
      return self.__DSTDIFF
    else:
      return ZERO

  def tzname(self, dt):
    return _time.tzname[self._isdst(dt)]

  def _isdst(self, dt):
    tt = (dt.year, dt.month, dt.day,
        dt.hour, dt.minute, dt.second,
        dt.weekday(), 0, 0)
    stamp = _time.mktime(tt)
    tt = _time.localtime(stamp)
    return tt.tm_isdst > 0
