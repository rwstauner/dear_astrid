# pylint: disable=wildcard-import,unused-wildcard-import,missing-docstring
# pylint: disable=too-many-public-methods

from __future__ import unicode_literals

from unittest import TestCase

import dear_astrid.json as daj
from dear_astrid.test.helpers import *

class TestJSON(TestCase):

  @classmethod
  def round_trip(cls, obj):
    return daj.json.loads(daj.dumps(obj))

  def assert_round_trip(self, obj, exp):
    self.assertEqual(self.round_trip(obj), dict(obj.copy(), **exp))

  def test_round_trip_helper(self):
    with self.assertRaises(AssertionError):
      self.assert_round_trip({'a': True}, {'a': False})

  def test_round_trip_basics(self):
    self.assert_round_trip({
        'title':        'squid',
        'priority':     2,
        'recurrence':   {'FREQ': 'DAILY', 'INTERVAL': 12},
        'completed':    None,
        'deleted':      None,
        'estimated':    8100,
        'elapsed':      0,
        'hooey':        True,
        'tags':         ['astrid', 'section 8', 'Hard cheese'],
        'notes':        "First note\nHere",
      },
      {} # no changes
    )

  def test_date_with_milliseconds(self):
    self.assert_round_trip(
      {'due': dtu(2014,  5, 10, 12,  0,  0, 402000) },
      {'due': '2014-05-10T12:00:00.402000+00:00' },
    )

  def test_date_with_zero_seconds(self):
    self.assert_round_trip(
      {'repeat_until': dtu(2014,  7, 19, 17, 55,  1), },
      {'repeat_until': '2014-07-19T17:55:01+00:00' },
    )
