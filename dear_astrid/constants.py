"""Constants for Astrid task attributes"""

import datetime

__all__ = [
  'FREQUENCY_UNITS',
  'RRULE_WEEK_DAYS',
  'WEEK_DAY_NAMES',
  'UTC',
]

# TODO: make these all lists?
FREQUENCY_UNITS = {
  'DAILY':   'day',
  'MONTHLY': 'month',
  'WEEKLY':  'week',
  'YEARLY':  'year',
}

RRULE_WEEK_DAYS = {
  'SU': 0,
  'MO': 1,
  'TU': 2,
  'WE': 3,
  'TH': 4,
  'FR': 5,
  'SA': 6,
}

WEEK_DAY_NAMES = (
  'Sunday',
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
)

# example from datetime.html#tzinfo-objects:

ZERO = datetime.timedelta(0)

class _UTC(datetime.tzinfo):
  # pylint: disable=missing-docstring,unused-argument

  def utcoffset(self, dt):
    return ZERO

  def tzname(self, dt):
    return "UTC"

  def dst(self, dt):
    return ZERO

UTC = _UTC()
