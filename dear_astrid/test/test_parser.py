# pylint: disable=wildcard-import,unused-wildcard-import,missing-docstring

from __future__ import unicode_literals

from nose.tools import *

from dear_astrid.parser import *
from dear_astrid.test.helpers import *

# shortcut
def one_task(fragment):
  return parse_xml(
    '<astrid format="2">{0}</astrid>'.format(fragment)
  )[0]

def test_parse_xml():
  assert_raises(AstridValueError, parse_xml, """<astrid format="3"/>""")

  assert_equal(
    one_task(
      '''
      <task title="squid" importance="2" dueDate="1399748400402"
      recurrence="" repeatUntil="0" deleted="0" completed="0"/>
      '''
    ),
    {
      'title':        'squid',
      'priority':     2,
      'due_date':     dtu(2014,  5, 10, 19,  0,  0, 402000),
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

  assert_equal(
    one_task(
      '''
  <task attachments_pushed_at="0" calendarUri="" classification="" completed="0" created="1370213954565" creatorId="0" deleted="0" detailsDate="0" dueDate="1370397301000" elapsedSeconds="0" estimatedSeconds="0" flags="0" hideUntil="1369724400000" historyFetch="0" historyHasMore="0" importance="2" is_public="0" is_readonly="0" lastSync="0" modified="1370214160202" notes="First note&#10;Here" postponeCount="0" pushedAt="0" recurrence="RRULE:FREQ=DAILY;INTERVAL=12" notificationFlags="6" lastNotified="0" notifications="1209600000" snoozeTime="0" repeatUntil="1405817701000" socialReminder="unseen" timerStart="0" title="repeat and remind" user="" activities_pushed_at="0" userId="0" remoteId="950575745031257201">
    <metadata created="1370214160080" deleted="0" key="alarm" value="1370214097446" value2="1" />
    <metadata created="0" deleted="0" key="tags-tag" value="section 8" value2="2153874380669753982" value3="950575745031257201" />
    <metadata created="0" deleted="0" key="tags-tag" value="Hard cheese" value2="799352962683373419" value3="950575745031257201" />
  </task>
      '''
    ),
    {
      'title':        'repeat and remind',
      'priority':     2,
      'due_date':     dtu(2013,  6,  5,  1, 55,  1),
      'recurrence':   {'FREQ': 'DAILY', 'INTERVAL': 12},
      'repeat_until': dtu(2014,  7, 20,  0, 55,  1),
      'completed':    None,
      'deleted':      None,
      'estimated':    0,
      'elapsed':      0,
      'notes':        "First note\nHere",
      'tags':         ['astrid', 'section 8', 'Hard cheese'],
    }
  )

  assert_equal(
    one_task(
      '''
  <task attachments_pushed_at="0" calendarUri="" classification="" completed="1370214214527" created="1370214183094" creatorId="0" deleted="0" detailsDate="0" dueDate="0" elapsedSeconds="0" estimatedSeconds="0" flags="0" hideUntil="0" historyFetch="0" historyHasMore="0" importance="3" is_public="0" is_readonly="0" lastSync="0" modified="1370214214638" notes="" postponeCount="0" pushedAt="0" recurrence="" notificationFlags="6" lastNotified="0" notifications="0" snoozeTime="0" repeatUntil="0" socialReminder="unseen" timerStart="0" title="Completed no priority" user="" activities_pushed_at="0" userId="0" remoteId="4514989953482146569" />
      '''
    ),
    {
      'title':        'Completed no priority',
      'priority':     3,
      'due_date':     None,
      'recurrence':   None,
      'repeat_until': None,
      'completed':    dtu(2013,  6,  2, 23,  3, 34, 527000),
      'deleted':      None,
      'estimated':    0,
      'elapsed':      0,
      'notes':        None,
      'tags':         ['astrid'],
    }
  )

  assert_equal(
    one_task(
      '''
  <task attachments_pushed_at="0" calendarUri="" classification="" completed="0" created="1370214247839" creatorId="0" deleted="0" detailsDate="0" dueDate="0" elapsedSeconds="0" estimatedSeconds="0" flags="0" hideUntil="0" historyFetch="0" historyHasMore="0" importance="0" is_public="0" is_readonly="0" lastSync="0" modified="1370234693330" notes="No, really" postponeCount="0" pushedAt="0" recurrence="" notificationFlags="6" lastNotified="0" notifications="0" snoozeTime="0" repeatUntil="0" socialReminder="unseen" timerStart="0" title="Really important" user="" activities_pushed_at="0" userId="0" remoteId="1480747625840088568">
    <metadata created="0" deleted="0" key="tags-tag" value="section 8" value2="2153874380669753982" value3="1480747625840088568" />
    <metadata created="0" deleted="0" key="tags-tag" value="nifty" value2="654272611227692712" value3="1480747625840088568" />
  </task>
      '''
    ),
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
    }
  )

  assert_equal(
    one_task(
      '''
  <task attachments_pushed_at="0" calendarUri="" classification="" completed="0" created="1370214439149" creatorId="0" deleted="0" detailsDate="0" dueDate="0" elapsedSeconds="2100" estimatedSeconds="8100" flags="0" hideUntil="0" historyFetch="0" historyHasMore="0" importance="1" is_public="0" is_readonly="0" lastSync="0" modified="1370234827340" notes="" postponeCount="0" pushedAt="0" recurrence="RRULE:FREQ=WEEKLY;INTERVAL=3;BYDAY=TH" notificationFlags="6" lastNotified="0" notifications="0" snoozeTime="0" repeatUntil="0" socialReminder="unseen" timerStart="0" title="Funky ch&amp;rs !n ^title a =b" user="" activities_pushed_at="0" userId="0" remoteId="583744141993888906">
    <metadata created="0" deleted="0" key="tags-tag" value="Hard cheese" value2="799352962683373419" value3="583744141993888906" />
  </task>
      '''
    ),
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
    }
  )

  assert_equal(
    one_task(
      '''
  <task attachments_pushed_at="0" calendarUri="" classification="" completed="1373263304672" created="1373263156134" creatorId="0" deleted="1373263316297" detailsDate="0" dueDate="0" elapsedSeconds="5100" estimatedSeconds="6900" flags="0" hideUntil="0" historyFetch="0" historyHasMore="0" importance="2" is_public="0" is_readonly="0" lastSync="0" modified="1373263316297" notes="Enough said" postponeCount="0" pushedAt="0" recurrence="" notificationFlags="6" lastNotified="0" notifications="1209600000" snoozeTime="0" repeatUntil="0" socialReminder="unseen" timerStart="0" title="Completed and deleted" user="" activities_pushed_at="0" userId="0" remoteId="4407620889991601387">
    <metadata created="1373263296778" deleted="0" key="alarm" value="1373263272089" value2="1" />
  </task>
      '''
    ),
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
    }
  )

def test_parse_timestamp():
  def t(stamp, exp):
    assert_equal(parse_timestamp(stamp).isoformat(), exp)

  t('1356116400000', '2012-12-21T19:00:00+00:00')
  t('1331413201000', '2012-03-10T21:00:01+00:00')
  t('1399748400000', '2014-05-10T19:00:00+00:00')
  t('1343754001000', '2012-07-31T17:00:01+00:00')
  t('1320562741000', '2011-11-06T06:59:01+00:00')
  t('1321124401000', '2011-11-12T19:00:01+00:00')
  t('1367420581000', '2013-05-01T15:03:01+00:00')
  t('1325534401000', '2012-01-02T20:00:01+00:00')
  t('1344826801000', '2012-08-13T03:00:01+00:00')
  t('1361889001001', '2013-02-26T14:30:01.001000+00:00')
  t('1361770201565', '2013-02-25T05:30:01.565000+00:00')
  t('1367434800203', '2013-05-01T19:00:00.203000+00:00')

  assert_raises(AstridValueError, parse_timestamp, 'sushi')


def test_parse_recurrence():
  def t(rr, exp):
    assert_equal(parse_recurrence(rr), exp)

  t('RRULE:FREQ=DAILY;INTERVAL=2', {'FREQ': 'DAILY', 'INTERVAL': 2})
  t('RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=SU',
    {'FREQ':'WEEKLY', 'INTERVAL': 1, 'BYDAY':'SU'})

  assert_raises(AstridValueError, parse_recurrence, '1367434800001')
