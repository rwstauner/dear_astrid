"""Parse Astrid xml backup file into simple data structures."""

from datetime import datetime
import re
from xml.dom import minidom

__all__ = [
  'AstridValueError',
  'parse_xml',
  'parse_task',
  'parse_timestamp',
  'parse_recurrence',
]

# TODO: ArgumentError?
class AstridValueError(Exception):
  """Value does not match expected format and cannot be parsed"""

  def __init__(self, key, val):
    Exception.__init__(self,
      'Unknown format for Astrid {}: {}'.format(key, val)
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

  # use method object as shortcut
  eattr = element.getAttribute

  # other fields: timerStart flags is_public hideUntil
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
    if extra.getAttribute('key') == 'tags-tag':
      task['tags'].append(extra.getAttribute('value'))
    # TODO: alarm

  return task


def parse_timestamp(stamp):
  """Parse astrid date/timestamp (milliseconds) to a datetime instance.

  This assumes a local time zone.
  Hopefully it's the same timezone as your astrid device.

  >>> parse_timestamp('1361905200321')
  datetime.datetime(2013, 2, 26, 12, 0, 0, 321000)

  >>> parse_timestamp('1389812400021').isoformat()
  '2014-01-15T12:00:00.021000'
  """

  if not stamp or stamp == '0':
    return

  try:
    stamp = int(stamp)
  except ValueError:
    raise AstridValueError('timestamp', stamp)

  # Astrid timestamps are milliseconds so divide by 1000
  # to get a unix timestamp (use '.0' to avoid rounding to whole numbers).
  # NOTE: It is not documented that datetime.fromtimestamp accepts fractions
  # so we might need to change this to call the constructor with ms * 1000.
  return datetime.fromtimestamp(stamp / 1000.0)


# TODO: consider parsing with https://github.com/collective/icalendar
def parse_recurrence(rule):
  """Convert astrid recurrence rule into dictionary

  >>> parse_recurrence('RRULE:FREQ=MONTHLY;INTERVAL=12')
  {'FREQ': 'MONTHLY', 'INTERVAL': '12'}
  """

  if not rule:
    return

  matched = re.match(r'^RRULE:((?:[A-Z]+=[^;]+;?)+)$', rule)
  if not matched:
    raise AstridValueError('recurrence', rule)

  # TODO: use constants for normalization?
  # TODO: see icalendar.prop (vWeekday, etc) for parsing?
  # TODO: cast to numbers
  return dict(s.split('=') for s in matched.group(1).split(';'))
