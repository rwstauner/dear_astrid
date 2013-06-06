"""
Convert Astrid tasks to RTM tasks.
"""

__docformat__ = 'reStructuredText'

from dear_astrid.constants import *

__all__ = [
  'format_date',
  'format_estimate',
  'format_priority',
  'format_repeat',
]


def format_date(dto):
  """Format datetime unambiguously (isoformat).

  ::

    >>> import datetime
    >>> format_date(datetime.datetime(2012, 12, 25, 13))
    '2012-12-25T13:00:00'

  """
  return dto.isoformat() if dto else None


def format_estimate(seconds):
  """Convert estimated seconds to estimated minutes.

  ::

    >>> format_estimate(3600)
    '60 min'

  """

  # Preserve fractions but only show them if non-zero.
  minutes = seconds / 60.0
  if minutes.is_integer():
    minutes = int(minutes)

  # TODO: "="
  return '{} min'.format(minutes)


def format_priority(priority_):
  """Convert astrid importance to rtm priority.

  Astrid uses 0 for most important and 3 for none.
  RTM uses 1 for highest priority and 4 for none.

  ::

    >>> format_priority(0)
    1
    >>> format_priority(3)
    4

  """

  # If not in the valid range set to no priority.
  if not priority_ in range(0, 3):
    priority_ = 3

  # off by one error ;-)
  # TODO: "!"
  return int(priority_) + 1


# TODO: warn about "repeat after" tasks that have notes
def format_repeat(repeat, until=None):
  """Transform RRULE dictionary into RTM repeat interval.

  ::

    >>> format_repeat({'FREQ': 'MONTHLY', 'INTERVAL': 6})
    'Every 6 months'

    >>> import datetime
    >>> repeat_until = datetime.datetime(2013, 6, 1)
    >>> format_repeat({'FREQ': 'DAILY', 'INTERVAL': 1}, repeat_until)
    'Every day until 2013-06-01T00:00:00'

  """

  parts = []

  interval = int(repeat.get('INTERVAL', 0))
  # ignore missing or zero
  if interval:
    unit = FREQUENCY_UNITS[repeat['FREQ']]
    if interval == 1:
      # 'Every year'
      parts.extend(['Every', unit])
    else:
      # 'Every 2 days'
      parts.extend(['Every', str(interval), unit + 's'])
  else:
    # 'Monthly'
    parts.append(repeat['FREQ'].capitalize())

  if 'BYDAY' in repeat:
    byday = repeat['BYDAY']
    dayname = byday
    if byday in RRULE_WEEK_DAYS:
      dayname = WEEK_DAY_NAMES[RRULE_WEEK_DAYS[byday]]
    # 'on Tuesday'
    parts.extend(['on', dayname])

  if until:
    parts.extend(['until', format_date(until)])

  return ' '.join(parts)
