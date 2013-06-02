"""Parse Astrid xml backup file into simple data structures."""

from datetime import datetime
import re

# TODO: ArgumentError?
class AstridValueError(Exception):
  """Value does not match expected format and cannot be parsed"""
  def __init__(self, key, val):
    Exception.__init__(self,
      'Unknown format for Astrid {}: {}'.format(key, val)
    )


def parse_timestamp(due):
  """Parse astrid date/timestamp value to object.

  >>> parse_timestamp('1361905200000')
  datetime.datetime(2013, 2, 26, 12, 0)

  >>> parse_timestamp('1389812400000').isoformat()
  '2014-01-15T12:00:00'
  """

  # astrid dates have three extra digits on the end (ms?)
  sec, tail = due[0:-3], due[-3:]

  # TODO: check for minimum length?
  # TODO: check that result is between 1900 and 2100?
  if not tail == '000':
    raise AstridValueError('timestamp', due)

  # NOTE: this uses local timezone, which is probably what you want
  # but I'm not entirely sure about that yet
  return datetime.fromtimestamp(int(sec))


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
  return dict(s.split('=') for s in matched.group(1).split(';'))
