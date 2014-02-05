"""
Parse Astrid xml backup file into simple data structures.
"""

from __future__ import unicode_literals

__docformat__ = 'reStructuredText'

from datetime import datetime
import re
from xml.dom import minidom

from dear_astrid.tzinfo import UTC

__all__ = [
  'AstridValueError',
  'parse_xml',
  'parse_task',
  'parse_timestamp',
  'parse_recurrence',
]


# should this subclass ValueError?
class AstridValueError(Exception):
  """Value does not match expected format and cannot be parsed."""

  def __init__(self, key, val):
    Exception.__init__(self,
      'Unknown format for Astrid {0}: {1}'.format(key, val)
    )


# TODO: allow passing alternate parse_* callables?
def parse_xml(xml=None):
  """Parse xml string into list of task dictionaries"""

  xml = minidom.parseString(xml)
  format_ = xml.getElementsByTagName('astrid')[0].getAttribute('format')

  if format_ != '2':
    raise AstridValueError('xml', format_)

  return [parse_task(t) for t in xml.getElementsByTagName('task')]


def parse_task(element):
  """Parse task element into a simple dictionaries."""

  # Use method object as shortcut.
  eattr = element.getAttribute

  # other fields: timerStart flags is_public hideUntil
  # created modified calendarUri details
  # flags2: remind when due?
  task = {
    'title':         eattr('title'),
    # astrid's "no priority" is 3
    'priority':      int(eattr('importance') or 3),
    'due_date':      parse_timestamp(eattr('dueDate')),
    'recurrence':    parse_recurrence(eattr('recurrence')),
    'repeat_until':  parse_timestamp(eattr('repeatUntil')),
    'completed':     parse_timestamp(eattr('completed')),
    'deleted':       parse_timestamp(eattr('deleted')),
    'estimated':     int(eattr('estimatedSeconds') or 0),
    'elapsed':       int(eattr('elapsedSeconds')   or 0),
    # tag everything with "astrid"
    'tags':          ['astrid'],
    'notes':         eattr('notes') or None,
  }

  for extra in element.getElementsByTagName('metadata'):
    key = extra.getAttribute('key')
    if key == 'tags-tag':
      task['tags'].append(extra.getAttribute('value'))
    elif key == 'alarm':
      if 'alarms' not in task:
        task['alarms'] = []
      task['alarms'].append(parse_timestamp(extra.getAttribute('value')))

  return task


def parse_timestamp(stamp):
  """Parse astrid date/timestamp (milliseconds) to a datetime instance.

  ::

    >>> parse_timestamp('1361905200321') # doctest: +ELLIPSIS
    datetime.datetime(2013, 2, 26, 19, 0, 0, 321000, tzinfo=...UTC...)

    >>> parse_timestamp('1389812400021').isoformat()
    '2014-01-15T19:00:00.021000+00:00'

  """

  if not stamp or stamp == '0':
    return

  # Astrid timestamps are milliseconds.  We could divide by 1000.0
  # but that gets us into floating point trouble.  Instead, separate
  # them while it's still a string, then put the fraction back on later.

  # separate seconds from milliseconds (last three digits)
  sec, ms = stamp[0:-3], stamp[-3:]

  try:
    sec = int(sec)
    ms  = int(ms)
  except ValueError:
    raise AstridValueError('timestamp', stamp)

  dt = datetime.fromtimestamp(sec, UTC())
  # put the microseconds on
  return dt.replace(microsecond=(ms * 1000))


# TODO: consider parsing with https://github.com/collective/icalendar
def parse_recurrence(rule):
  """Convert astrid recurrence rule into dictionary for simplicity.

  ::

    >>> d = parse_recurrence('RRULE:FREQ=MONTHLY;INTERVAL=12')
    >>> d == {'FREQ': 'MONTHLY', 'INTERVAL': 12}
    True

  """

  if not rule:
    return

  matched = re.match(r'^RRULE:((?:[A-Z]+=[^;]+;?)+)$', rule)
  if not matched:
    raise AstridValueError('recurrence', rule)

  # TODO: use constants for normalization?
  # TODO: see icalendar.prop (vWeekday, etc) for parsing?

  recur = dict(s.split('=') for s in matched.group(1).split(';'))

  # Cast numeric entries for ease of use.
  for key in ('INTERVAL',):
    if key in recur:
      recur[key] = int(recur[key])

  return recur
