# pylint: disable=wildcard-import,unused-wildcard-import,missing-docstring

from datetime import datetime

from nose.tools import *

from dear_astrid.rtm import *

def test_format_date():
  def t(dto, exp):
    assert_equal(format_date(dto), exp)

  t(datetime(1997,  3, 26), '1997-03-26T00:00:00')
  t(datetime(2012, 11,  3, 12, 34, 56, 789123), '2012-11-03T12:34:56.789123')

  t(datetime.fromtimestamp(1322207664), '2011-11-25T00:54:24')
  t(datetime.fromtimestamp(1342207664.579), '2012-07-13T12:27:44.579000')


