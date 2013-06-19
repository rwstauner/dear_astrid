"""Constants for Astrid task attributes"""

__all__ = [
  'FREQUENCY_UNITS',
  'RRULE_WEEK_DAYS',
  'WEEK_DAY_NAMES',
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
