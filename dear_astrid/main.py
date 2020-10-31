"""
Simple CLI app to parse and convert Astrid backup file.
"""

from __future__ import print_function, unicode_literals

import argparse
import sys

from dear_astrid import __version__
from dear_astrid.parser import parse_xml

__all__ = []

# TODO: entry_points?
actions = {}
def action(func=None, name=None):
  """Function decorator for adding actions to dispatch table."""
  if func is None:
    return lambda f: action(f, name.encode('ascii'))
  if name is None:
    name = func.__name__

  # Register in dispatch table.
  actions[name] = func

  return func

@action
def rtm_to_astrid(content):
  from dear_astrid.rtm.parse import parse_export
  from dear_astrid.formatter import format_xml
  tasks = parse_export(content)
  print(format_xml(tasks))

@action
def json(content):
  import dear_astrid.json
  tasks = parse_xml(content)
  # TODO: Make kwargs configurable?  Use a separate raw_json action?
  print(dear_astrid.json.dumps(tasks, indent=2))

@action(name='print')
def print_tasks(content):
  tasks = parse_xml(content)
  for task in tasks:
    print("\n  {0}".format(task.get('title', '(unspecified)')))

    for key in sorted(task.keys()):
      if key == 'title':
        continue

      val = task[key]
      if not val:
        continue

      print("    {0}: {1}".format(key, val))

def main():
  """Parse backup file and convert the tasks to another format."""

  argp = argparse.ArgumentParser(description = main.__doc__)
  argp.add_argument('action', default='print', choices=actions.keys(),
    help='Action: What to do with parsed tasks')
  argp.add_argument('file', help='Path to backup file')
  argp.add_argument('--version', action='version', version='%(prog)s ' + __version__)
  args = argp.parse_args()

  content = (sys.stdin if args.file == "-" else open(args.file)).read()

  if args.action in actions:
    actions[args.action](content)
  else:
    raise 'Unknown action: {0}'.format(args.action)
