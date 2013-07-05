# pylint: disable=wildcard-import,unused-wildcard-import,missing-docstring
# pylint: disable=no-member

from __future__ import absolute_import

from unittest import TestCase

from nose.tools import *
from mock import *

from dear_astrid.rtm.importer import *

try:
  raw_input
  INPUT_FUNC = '__builtin__.raw_input'
except NameError:
  INPUT_FUNC = 'builtins.input'

class TestRTMImport(TestCase):
  def setUp(self):
    self.patches = dict(
      time = patch('time.sleep'),
      rtm  = patch('rtm.createRTM'),
      browser = patch('webbrowser.open'),
      prompt  = patch(INPUT_FUNC)
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

    # Prepare to test Exceptions raised on login test.
    login = Mock()
    login.test.login.side_effect = AuthError('oops')
    self.mocks['rtm'].return_value = login

    def reset():
      for mock in (login, self.mocks['rtm']):
        mock.reset_mock()

    reset()

    auth = BaseAuth(1, 2, 3)
    assert_raises(AuthError, auth.auth)
    self.mocks['rtm'].assert_called_once_with(1, 2, 3)
    login.assert_has_calls([call.test.login()])

    reset()

    assert_raises(AuthError, auth.api)
    self.mocks['rtm'].assert_called_once_with(1, 2, 3)
    login.assert_has_calls([call.test.login()])

    reset()

    try:
      auth.api(test_login=False)
    except AuthError:
      assert False
    else:
      assert True

    assert not login.called

  def test_cli_auth(self):
    url = 'jelly://bean'
    token = 'cookies'

    api = Mock()
    api.getAuthURL.return_value = url
    api.getToken.return_value = token

    self.mocks['rtm'].return_value = api

    # Don't print during the tests
    CLIAuth.message = Mock()

    api = CLIAuth('K', 'S').auth()

    self.mocks['rtm'].assert_has_calls([
      call('K', 'S', 'dear_astrid'),
      # no test.login()
      call().getAuthURL(),
      call().getToken(),
      call('K', 'S', token),
      call().test.login(),
    ])

    self.mocks['browser'].called_once_with(url, True, True)

    # Url printed to screen.
    assert CLIAuth.message.call_args[0][2] == url

    assert self.mocks['prompt'].call_count == 1
    assert self.mocks['prompt'].call_args[0][0].startswith('Press Enter')

    # TODO: assert_raises
