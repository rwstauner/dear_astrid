"""
Convert Astrid tasks to RTM tasks.
"""

__docformat__ = 'reStructuredText'

import datetime

from dear_astrid.constants import *
from dear_astrid.tzinfo    import *

__all__ = [
  'format_task',
  'format_date',
  'format_estimate',
  'format_priority',
  'format_repeat',
]

# TODO: rtm.tasks.complete()
# TODO: rtm.tasks.delete()
def format_task(oldtask):
  """Reformat task dictionary to make it ready to use with RTM."""

  newtask = {
    'name':     oldtask['title'],
    'notes':    oldtask['notes'],
    'priority': format_priority(oldtask['priority']),
    'repeat':   format_repeat(oldtask['recurrence'], oldtask['repeat_until']),
    # make a copy so we can modify it
    'tags':     list(oldtask['tags']),
  }

  # datetime
  for ts in ('due_date',):
    newtask[ts] = format_date(oldtask[ts])

  # seconds to minutes
  # RTM doesn't do 'elapsed'.
  for ts in ('estimated',):
    newtask[ts] = format_estimate(oldtask[ts])

  # bool (RTM doesn't take dates for these).
  for ts in ('completed', 'deleted'):
    newtask[ts] = bool(oldtask[ts])
    if newtask[ts]:
      newtask['tags'].append('astrid-' + ts)

  # Build up the 'smart add' string for inspection.
  smart = [newtask['name']]

  if newtask['due_date'] is not None:
    smart.append('^' + format_date(oldtask['due_date'], local=True))

  if newtask['priority'] is not None:
    smart.append('!' + str(newtask['priority']))

  smart.extend('#' + t for t in newtask['tags'])

  if newtask['repeat'] is not None:
    smart.append('*' + format_repeat(
      oldtask['recurrence'], oldtask['repeat_until'], local=True,
    ))

  if newtask['estimated']:
    smart.append('=' + newtask['estimated'])

  newtask['smart_add'] = ' '.join(smart)

  return newtask


def format_date(dto, local=False):
  """Format datetime unambiguously (isoformat).

  ::

    >>> import datetime
    >>> format_date(datetime.datetime(2012, 12, 25, 13))
    '2012-12-25T13:00:00Z'

  """
  if not dto:
    return

  # RTM api docs say everything should be UTC (all examples end with 'Z').
  # The docs don't mention microsecond, so ignore that
  # (besides, the astrid dates that have microseconds are 'completed'
  # and 'deleted' and we can't preserve those anyway).
  fmt = '%Y-%m-%dT%H:%M:%SZ'

  if local:
    # If we do want local, strip the Z from the format.
    fmt = fmt[:-1]
    dto = dto.astimezone(LocalTimezone())

  return dto.strftime(fmt)


def format_estimate(seconds):
  """Convert estimated seconds to estimated minutes.

  ::

    >>> format_estimate(3600)
    '60 min'

  """

  if not seconds:
    return

  # Preserve fractions but only show them if non-zero.
  minutes = seconds / 60.0
  if minutes.is_integer():
    minutes = int(minutes)

  # TODO: "="
  return '{0} min'.format(minutes)


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
def format_repeat(repeat, until=None, local=False):
  """Transform RRULE dictionary into RTM repeat interval.

  ::

    >>> format_repeat({'FREQ': 'MONTHLY', 'INTERVAL': 6})
    'Every 6 months'

    >>> import datetime
    >>> repeat_until = datetime.datetime(2013, 6, 1)
    >>> format_repeat({'FREQ': 'DAILY', 'INTERVAL': 1}, repeat_until)
    'Every day until 2013-06-01T00:00:00Z'

  """

  if not repeat:
    return

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
    parts.extend(['until', format_date(until, local)])

  return ' '.join(parts)
