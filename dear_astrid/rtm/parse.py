"""
Parse RTM export into simple data structures.
"""

from __future__ import unicode_literals

__docformat__ = 'reStructuredText'

import dear_astrid.json as json

__all__ = [
  'parse_export',
]

def parse_export(content):
  """Parse rtm export into dict."""

  data = json.loads(content)
  notes = data.get('notes', [])
  tasks = []
  for task in data['tasks']:
    newtask = {
      'title': task['name'],
      'priority': parse_priority(task.get('priority', 'P4')),
      'due_date': parse_date(task.get('date_due')),
      'start_date': parse_date(task.get('date_start')),
      'recurrence': parse_repeat(task.get('repeat'), task.get('repeat_every')),
      'created': parse_date(task['date_created']),
      'completed': parse_date(task.get('date_completed')),
      'deleted': parse_date(task.get('date_trashed')),
      'tags': task.get('tags', []),
      'notes': parse_notes([n for n in notes if n['series_id'] == task['series_id']])
    }
    tasks.append(newtask)

  return tasks

def parse_date(date):
  """Parse date int string into to date int (no-op)."""
  if date is None:
    return 0
  return int(date)

def parse_notes(notes):
  """Join note content into a string for astrid."""

  return "\n".join(
    ["\n".join([n.get('title'), n.get('content')]) for n in notes]
  )

def parse_priority(priority):
  """Parse RTM priority into astrid importance.

  Astrid uses 0 for most important and 3 for none.
  RTM uses 1 for highest priority and 4 for none.

  ::

    >>> parse_priority("P1")
    0
    >>> parse_priority("PN")
    3

  """

  num = priority[1:]
  if num == "N":
    return 3
  else:
    return int(num) - 1

def parse_repeat(repeat, every):
  """Parse repeate into astrid RRULE."""
  if repeat is None:
    return ""
  return "RRULE:" + repeat + (';FROM=COMPLETION' if not every else '')
