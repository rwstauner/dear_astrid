"""
Simple CLI app to parse and convert Astrid backup file.
"""

from __future__ import print_function, unicode_literals

import argparse

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
def json(tasks):
  import dear_astrid.json
  # TODO: Make kwargs configurable?  Use a separate raw_json action?
  print(dear_astrid.json.dumps(tasks, indent=2))

@action(name='print')
def print_tasks(tasks):
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
  """Parse Astrid backup xml file and convert the tasks to another format."""

  argp = argparse.ArgumentParser(description = main.__doc__)
  argp.add_argument('action', default='print', choices=actions.keys(),
    help='Action: What to do with parsed tasks')
  argp.add_argument('file', help='Path to Astrid backup xml file')
  args = argp.parse_args()

  tasks = parse_xml(open(args.file).read())

  if args.action in actions:
    actions[args.action](tasks)
  else:
    raise 'Unknown action: {0}'.format(args.action)
