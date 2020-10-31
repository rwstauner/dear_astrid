# pylint: disable=wildcard-import,unused-wildcard-import,missing-docstring
# pylint: disable=undefined-variable,line-too-long,invalid-name

from __future__ import unicode_literals

from nose.tools import *

from dear_astrid.formatter import *
from dear_astrid.parser import *
from dear_astrid.test.helpers import *

# shortcut
def one_task(fragment):
  return parse_xml(
    '<astrid format="2">{0}</astrid>'.format(fragment)
  )[0]

class TestFormatXML(TestCase):
  # pylint: disable=too-many-public-methods,no-member

  def assert_task_parses(self, xml, exp):
    with timezone('UTC'):
      self.assert_equal(one_task(xml), exp)

  def assert_round_trip(self, task):
    xml = format_task(task)
    tags = ['astrid']
    tags.extend(task['tags'])
    task['tags'] = tags
    self.assert_task_parses(xml, task)

  def test_round_trip(self):
    self.assert_round_trip({
      'title':        'squid',
      'priority':     2,
      'due_date':     dtu(2014, 5, 10, 19, 0, 0, 402000),
      'recurrence':   None,
      'repeat_until': None,
      'completed':    None,
      'deleted':      None,
      'estimated':    0,
      'elapsed':      0,
      'tags':         [],
      'notes':        None,
    })

    self.assert_round_trip({
      'title':        'squidly',
      'priority':     3,
      'due_date':     dtu(2014, 5, 10, 19, 0, 0, 402000),
      'recurrence':   {"FREQ": "DAILY", "INTERVAL": 12},
      'repeat_until': None,
      'completed':    dtu(2014, 6, 10, 19, 0, 0, 402000),
      'deleted':      None,
      'estimated':    0,
      'elapsed':      0,
      'tags':         ["taggy"],
      'notes':        "foo",
    })

