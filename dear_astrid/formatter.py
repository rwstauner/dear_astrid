"""
Format Astrid xml backup file from simple data structures.
"""

from __future__ import unicode_literals

__docformat__ = 'reStructuredText'

import datetime
import xml.sax.saxutils as xml

from dear_astrid.tzinfo import UTC

__all__ = [
  'format_xml',
  'format_task',
]


def format_xml(tasks):
  """Produce xml from list of task dictionaries"""

  xml_lines = [
    '<?xml version="1.0" encoding="utf-8" ?>',
    '<astrid version="306" format="2">',
  ]

  for task in tasks:
    xml_lines.append(format_task(task))

  xml_lines.append('</astrid>')

  return "\n".join(xml_lines).encode('utf-8')

def quoteattr(value):
  """Quote value for use as an xml attribute."""
  if value is None:
    value = ''
  if not isinstance(value, unicode):
    value = unicode(value)
  return xml.quoteattr(value)

def format_task(task):
  """Format <task/> xml tag from task."""

  attr = {
    'title': task.get('title'),
    'importance': task.get('priority', 3),
    'dueDate': format_date(task.get('due_date')),
    'hideUntil': format_date(task.get('start_date')),
    'recurrence': format_recurrence(task.get('recurrence')),
    'repeatUntil': 0,
    'created': format_date(task.get('created', 0)),
    'completed': format_date(task.get('completed', 0)),
    'deleted': format_date(task.get('deleted', 0)),
    'elapsedSeconds': 0,
    'estimatedSeconds': 0,
    'notes': task.get('notes'),

    'attachments_pushed_at': "0",
    'calendarUri': "",
    'classification': "",
    'creatorId': "0",
    'details': " | ",
    'detailsDate': "0",
    'flags': "0",
    'historyFetch': "0",
    'historyHasMore': "0",
    'is_public': "0",
    'is_readonly': "0",
    'lastSync': "0",
    'modified': "0",
    'postponeCount': "0",
    'pushedAt': "0",
    'notificationFlags': "2",
    'lastNotified': "0",
    'notifications': "0",
    'snoozeTime': "0",
    'socialReminder': "unseen",
    'timerStart': "0",
    'user': "{}",
    'activities_pushed_at': "0",
    'userId': "0",
    'remoteId': "0",
  }
  parts = ['<task']

  for key, value in attr.items():
    parts.append('{0}={1}'.format(key, quoteattr(value)))

  parts.append('>')
  for tag in task.get('tags', []):
    # I don't know what value2 is supposed to be but it looks like a string of
    # numbers.
    value2 = "".join([str(ord(x)) for x in tag])
    parts.append('<metadata key="tags-tag" value={} value2={} />'.format(quoteattr(tag), quoteattr(value2)))

  if not task.get('start_date', 0) == 0:
    parts.append('<metadata key="alarm" value={} value2="1" />'.format(quoteattr(task['start_date'])))

  parts.append('</task>')

  return " ".join(parts)

EPOCH = datetime.datetime.fromtimestamp(0, UTC())

def format_date(dt):
  """Format datetime value into astrid stamp."""

  if isinstance(dt, datetime.datetime):
    # Produce %s in UTC without getting offset by the local time.
    return str(int((dt - EPOCH).total_seconds()*1000)) #+ str(dt.microsecond/1000)

  return dt

def format_recurrence(recur):
  if isinstance(recur, dict):
    return "RRULE:" + ';'.join(["{0}={1}".format(k, v) for (k,v) in recur.items()])
  return recur
