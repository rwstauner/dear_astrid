# pylint: disable=wildcard-import,unused-wildcard-import,missing-docstring

from __future__ import absolute_import
from nose.tools import *
import datetime

from dear_astrid.parser import *

# shortcut
def one_task(fragment):
  return parse_xml(
    '<astrid format="2"><task {}></task></astrid>'.format(fragment)
  )[0]

def test_parse_xml():
  assert_raises(AstridValueError, parse_xml, """<astrid format="3"/>""")

  assert_equal(
    one_task(
      '''title="squid" importance="2" dueDate="1399748400402"
      recurrence="" repeatUntil="0" deleted="0" completed="0"
      '''
    ),
    {
      'title':        u'squid',
      'priority':     2,
      'due_date':     datetime.datetime(2014, 5, 10, 12, 0, 0, 402000),
      'recurrence':   None,
      'repeat_until': None,
      'completed':    None,
      'deleted':      None,
      'estimated':    0,
      'elapsed':      0,
      'tags':         ['astrid'],
      'notes':        None,
    }
  )


def test_parse_timestamp():
  def t(stamp, exp):
    assert_equal(parse_timestamp(stamp).isoformat(), exp)

  t('1356116400000', '2012-12-21T12:00:00')
  t('1331413201000', '2012-03-10T14:00:01')
  t('1399748400000', '2014-05-10T12:00:00')
  t('1343754001000', '2012-07-31T10:00:01')
  t('1320562741000', '2011-11-05T23:59:01')
  t('1321124401000', '2011-11-12T12:00:01')
  t('1367420581000', '2013-05-01T08:03:01')
  t('1325534401000', '2012-01-02T13:00:01')
  t('1344826801000', '2012-08-12T20:00:01')
  t('1361889001001', '2013-02-26T07:30:01.001000')
  t('1361770201565', '2013-02-24T22:30:01.565000')
  t('1367434800203', '2013-05-01T12:00:00.203000')

  assert_raises(AstridValueError, parse_timestamp, 'sushi')


def test_parse_recurrence():
  def t(rr, exp):
    assert_equal(parse_recurrence(rr), exp)

  t('RRULE:FREQ=DAILY;INTERVAL=2', {'FREQ': 'DAILY', 'INTERVAL': '2'})
  t('RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=SU',
    {'FREQ':'WEEKLY', 'INTERVAL':'1', 'BYDAY':'SU'})

  assert_raises(AstridValueError, parse_recurrence, '1367434800001')
