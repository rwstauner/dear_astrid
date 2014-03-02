# pylint: disable=wildcard-import,unused-wildcard-import,missing-docstring
# pylint: disable=too-many-public-methods,no-member

from __future__ import unicode_literals

from datetime import datetime

from nose.tools import *

from dear_astrid.rtm import *
from dear_astrid.test.helpers import *

class TestFormatTask(TestCase):
  def assert_format(self, tsk, exp):
    with timezone(exp.pop('tz', None)):
      tsk = format_task(tsk)
      # test smart_add separately to avoid excessively large diffs
      smarts = [ d.pop('smart_add', None) for d in (tsk, exp) ]
      self.assert_equal(tsk, exp)
      self.assert_equal(*smarts)

  def test_basic_task(self):
    self.assert_format(
    {
      'title':        'squid',
      'priority':     2,
      'due_date':     dtu(2014,  5, 10, 12,  0,  0, 402000),
      'recurrence':   None,
      'repeat_until': None,
      'completed':    None,
      'deleted':      None,
      'estimated':    0,
      'elapsed':      0,
      'tags':         ['astrid'],
      'notes':        None,
    },
    {
      'name':         'squid',
      'priority':     3,
      'due_date':     '2014-05-10T12:00:00Z',
      'repeat':       None,
      'completed':    False,
      'deleted':      False,
      'estimated':    None,
      'tags':         ['astrid'],
      'notes':        None,
      'tz':           'US/Eastern',
      'smart_add':    'squid ^2014-05-10T08:00:00 !3 #astrid',
    },
    )

  def test_repeat_and_remind(self):
    self.assert_format(
    {
      'title':        'repeat and remind',
      'priority':     2,
      'due_date':     dtu(2013,  6,  4, 18, 55,  1),
      'recurrence':   {'FREQ': 'DAILY', 'INTERVAL': 12},
      'repeat_until': dtu(2014,  7, 19, 17, 55,  1),
      'completed':    None,
      'deleted':      None,
      'estimated':    0,
      'elapsed':      0,
      'notes':        "First note\nHere",
      'tags':         ['astrid', 'section 8', 'Hard cheese'],
    },
    {
      'name':         'repeat and remind',
      'priority':     3,
      'due_date':     '2013-06-04T18:55:01Z',
      'repeat':       'Every 12 days until 2014-07-19T17:55:01Z',
      'completed':    False,
      'deleted':      False,
      'estimated':    None,
      'notes':        "First note\nHere",
      'tags':         ['astrid', 'section 8', 'Hard cheese', 'astrid-notes'],
      'tz':           'America/Phoenix',
      'smart_add':    (
        'repeat and remind ^2013-06-04T11:55:01'
        ' !3 #astrid #section 8 #Hard cheese #astrid-notes'
        ' *Every 12 days until 2014-07-19T10:55:01'
      ),
    },
    )

  def test_completed_no_priority(self):
    self.assert_format(
    {
      'title':        'Completed no priority',
      'priority':     3,
      'due_date':     None,
      'recurrence':   None,
      'repeat_until': None,
      'completed':    datetime(2013,  6,  2, 16,  3, 34, 527000),
      'deleted':      None,
      'estimated':    0,
      'elapsed':      0,
      'notes':        None,
      'tags':         ['astrid'],
    },
    {
      'name':         'Completed no priority',
      'priority':     4,
      'due_date':     None,
      'repeat':       None,
      'completed':    True,
      'deleted':      False,
      'estimated':    None,
      'notes':        None,
      'tags':         ['astrid', 'astrid-completed'],
      'smart_add':    'Completed no priority !4 #astrid #astrid-completed',
    },
    )

  def test_really_important(self):
    self.assert_format(
    {
      'title':        'Really important',
      'priority':     0,
      'due_date':     None,
      'recurrence':   None,
      'repeat_until': None,
      'completed':    None,
      'deleted':      None,
      'estimated':    0,
      'elapsed':      0,
      'notes':        'No, really',
      'tags':         ['astrid', 'section 8', 'nifty'],
    },
    {
      'name':         'Really important',
      'priority':     1,
      'due_date':     None,
      'repeat':       None,
      'completed':    False,
      'deleted':      False,
      'estimated':    None,
      'notes':        'No, really',
      'tags':         ['astrid', 'section 8', 'nifty', 'astrid-notes'],
      'smart_add':
        'Really important !1 #astrid #section 8 #nifty #astrid-notes',
    },
    )

  def test_funky_chars(self):
    self.assert_format(
    {
      'title':        'Funky ch&rs !n ^title a =b',
      'priority':     1,
      'due_date':     None,
      'recurrence':   dict(FREQ='WEEKLY', INTERVAL=3, BYDAY='TH'),
      'repeat_until': None,
      'completed':    None,
      'deleted':      None,
      'estimated':    8100,
      'elapsed':      2100,
      'notes':        None,
      'tags':         ['astrid', 'Hard cheese'],
    },
    {
      'name':         'Funky ch&rs !n ^title a =b',
      'priority':     2,
      'due_date':     None,
      'repeat':       'Every 3 weeks on Thursday',
      'completed':    False,
      'deleted':      False,
      'estimated':    '135 min',
      'notes':        None,
      'tags':         ['astrid', 'Hard cheese'],
      'smart_add':    (
        'Funky ch&rs \!n \^title a \=b'
        ' !2 #astrid #Hard cheese'
        ' *Every 3 weeks on Thursday'
        ' =135 min'
      ),
    },
    )

  def test_completed_and_deleted(self):
    self.assert_format(
    {
      'title':        'Completed and deleted',
      'priority':     2,
      'due_date':     None,
      'recurrence':   None,
      'repeat_until': None,
      'completed':    dtu(2013,  7,  8,  6,  1, 44, 672000),
      'deleted':      dtu(2013,  7,  8,  6,  1, 56, 297000),
      'estimated':    6900,
      'elapsed':      5100,
      'notes':        'Enough said',
      'tags':         ['astrid'],
    },
    {
      'name':         'Completed and deleted',
      'priority':     3,
      'due_date':     None,
      'repeat':       None,
      'completed':    True,
      'deleted':      True,
      'estimated':    '115 min',
      'notes':        'Enough said',
      'tags':         ['astrid', 'astrid-completed', 'astrid-deleted', 'astrid-notes'],
      'smart_add':    (
        'Completed and deleted'
        ' !3 #astrid #astrid-completed #astrid-deleted #astrid-notes'
        ' =115 min'
      ),
    },
    )

def test_format_date():
  def t(dto, exp, tz, loc):
    assert_equal(format_date(dto), exp)
    with timezone(tz):
      assert_equal(format_date(dto, local=True), loc)

  # TODO: test local

  t(dtu(1997,  3, 26,  0,  0,  0,      0), '1997-03-26T00:00:00Z',
    'America/Los_Angeles',                 '1997-03-25T16:00:00')
  t(dtu(2012, 11, 30, 12, 34, 56, 789123), '2012-11-30T12:34:56Z',
    'America/Chicago',                     '2012-11-30T06:34:56')

  t(datetime.utcfromtimestamp(1322207664).replace(tzinfo=UTC()),
    '2011-11-25T07:54:24Z',
    'UTC', '2011-11-25T07:54:24')
  t(datetime.utcfromtimestamp(1342207664.579).replace(tzinfo=UTC()),
    '2012-07-13T19:27:44Z',
    # from the tzset(3) man page
    'NZST-12:00:00NZDT-13:00:00,M10.1.0,M3.3.0', '2012-07-14T07:27:44')

def test_format_estimate():
  def t(sec, exp):
    assert_equal(format_estimate(sec), exp)

  t(300,      '5 min')
  t(3600,    '60 min')
  t(30,     '0.5 min')
  t(510,    '8.5 min')
  t(86400, '1440 min')

def test_format_priority():
  def t(pri, exp):
    assert_equal(format_priority(pri), exp)

  t(0, 1)
  t(1, 2)
  t(2, 3)
  t(3, 4)
  # out of bounds: no priority
  t(-1, 4)
  t(5, 4)
  t('squid', 4)


def test_format_repeat():
  def t(rep, exp):
    assert_equal(format_repeat(rep), exp)

  # no INTERVAL
  t({'FREQ': 'DAILY'}, 'Daily')

  t({'FREQ': 'YEARLY',  'INTERVAL': 1}, 'Every year')
  t({'FREQ': 'MONTHLY', 'INTERVAL': 2}, 'Every 2 months')

  t({'FREQ': 'WEEKLY',  'INTERVAL': 2, 'BYDAY': 'TU'},
    'Every 2 weeks on Tuesday')

  # Return unknown BYDAY as is.
  t({'FREQ': 'MONTHLY', 'INTERVAL': 3, 'BYDAY': 'CHEESE'},
    'Every 3 months on CHEESE')
