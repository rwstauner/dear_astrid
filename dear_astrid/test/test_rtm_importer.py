# pylint: disable=wildcard-import,unused-wildcard-import,missing-docstring
# pylint: disable=no-member

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

  def test_base_auth(self):
    api = BaseAuth('k', 's', 't').auth()
    self.mocks['rtm'].assert_called_once_with('k', 's', 't')
    api.test.login.assert_called_once_with()

    class AuthError(Exception):
      pass

    login = Mock()
    login.test.login.side_effect = AuthError('oops')
    self.mocks['rtm'].return_value = login

    auth = BaseAuth(1, 2, 3)
    assert_raises(AuthError, auth.auth)
    assert_raises(AuthError, auth.api)

    try:
      auth.api(test_login=False)
    except AuthError:
      assert False
    else:
      assert True
