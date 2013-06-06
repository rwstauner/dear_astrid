# pylint: disable=wildcard-import,unused-wildcard-import,missing-docstring

from datetime import datetime

from nose.tools import *

from dear_astrid.rtm import *

def test_format_task():

  assert_equal(
    format_task({
      'title':        u'squid',
      'priority':     2,
      'due_date':     datetime(2014,  5, 10, 12,  0,  0, 402000),
      'recurrence':   None,
      'repeat_until': None,
      'completed':    None,
      'deleted':      None,
      'estimated':    0,
      'elapsed':      0,
      'tags':         ['astrid'],
      'notes':        None,
    }),
    {
      'name':         u'squid',
      'priority':     3,
      'due_date':     '2014-05-10T12:00:00.402000',
      'repeat':       None,
      'completed':    False,
      'deleted':      False,
      'estimated':    None,
      'tags':         ['astrid'],
      'notes':        None,
    }
  )

def test_format_date():
  def t(dto, exp):
    assert_equal(format_date(dto), exp)

  t(datetime(1997,  3, 26), '1997-03-26T00:00:00')
  t(datetime(2012, 11,  3, 12, 34, 56, 789123), '2012-11-03T12:34:56.789123')

  t(datetime.fromtimestamp(1322207664), '2011-11-25T00:54:24')
  t(datetime.fromtimestamp(1342207664.579), '2012-07-13T12:27:44.579000')

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
