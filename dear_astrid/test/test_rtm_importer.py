# pylint: disable=wildcard-import,unused-wildcard-import,missing-docstring

from __future__ import absolute_import

from unittest import TestCase

from nose.tools import *
from mock import *

from dear_astrid.rtm.importer import *

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
    imp = Importer(['task'])
    imp._rtm = Mock()

    assert not self.mocks['time'].called

    # Assert that it is in fact our mock object.
    assert_equal(imp.rtm, imp._rtm)

    self.mocks['time'].assert_called_once_with(1)

    # Test chaining method calls.
    imp.rtm.foo.bar

    self.mocks['time'].assert_has_calls([ call(1), call(1) ])

    # Not used this time.
    assert not self.mocks['rtm'].called

  def test_deobfuscator(self):
    imp = Importer(['task'])

    imp.key = 'a92'
    assert imp.key == '21a'

    imp.secret = 'deadbeef'
    assert imp.secret == '56253667'
