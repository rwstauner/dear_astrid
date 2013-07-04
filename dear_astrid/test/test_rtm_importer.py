# pylint: disable=wildcard-import,unused-wildcard-import,missing-docstring

from __future__ import absolute_import

from unittest import TestCase

from nose.tools import *
from mock import *

from dear_astrid.rtm.importer import Importer as rtmimp

class TestRTMImport(TestCase):
  def setUp(self):
    self.patches = dict(
      time = patch('time.sleep'),
      rtm  = patch('rtm.createRTM'),
    )
    self.mocks = dict()
    for (k, v) in self.patches.items():
      self.mocks[k] = v.start()

  def test_sleep_before_rtm(self):
    imp = rtmimp(['task'])
    imp._rtm = Mock()

    assert not self.mocks['time'].called

    # assert that it is our mock object
    assert_equal(imp.rtm, imp._rtm)

    self.mocks['time'].assert_called_once_with(1)

    # test calling other methods
    imp.rtm.foo.bar

    self.mocks['time'].assert_has_calls([ call(1), call(1) ])

    # not used this time
    assert not self.mocks['rtm'].called
