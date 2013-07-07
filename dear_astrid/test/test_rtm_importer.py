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
INPUT_MOCK = MagicMock()

@patch('time.sleep')
@patch('rtm.createRTM')
@patch('webbrowser.open')
@patch(INPUT_FUNC, new=INPUT_MOCK)
class TestRTMImport(TestCase):

  def test_sleep_before_rtm(self, *args):
    imp = Importer(['task'])
    imp._rtm = Mock()

    assert not time.sleep.called

    # Assert that it is in fact our mock object.
    assert_equal(imp.rtm, imp._rtm)

    time.sleep.assert_called_once_with(1)

    # Test chaining method calls.
    imp.rtm.foo.bar

    time.sleep.assert_has_calls([ call(1), call(1) ])

    # Not used this time.
    assert not rtm.createRTM.called

  def test_deobfuscator(self, *args):
    imp = Importer(['task'])

    imp.key = 'a92'
    assert imp.key == '21a'

    imp.secret = 'deadbeef'
    assert imp.secret == '56253667'

  def test_base_auth(self, *args):
    api = BaseAuth('k', 's', 't').auth()
    rtm.createRTM.assert_called_once_with('k', 's', 't')
    api.test.login.assert_called_once_with()

    # Prepare to test Exceptions raised on login test.
    login = Mock()
    login.test.login.side_effect = AuthError('oops')
    rtm.createRTM.return_value = login

    def reset():
      for mock in (login, rtm.createRTM):
        mock.reset_mock()

    reset()

    auth = BaseAuth(1, 2, 3)
    assert_raises(AuthError, auth.auth)
    rtm.createRTM.assert_called_once_with(1, 2, 3)
    login.assert_has_calls([call.test.login()])

    reset()

    assert_raises(AuthError, auth.api)
    rtm.createRTM.assert_called_once_with(1, 2, 3)
    login.assert_has_calls([call.test.login()])

    reset()

    try:
      auth.api(test_login=False)
    except AuthError:
      assert False
    else:
      assert True

    assert not login.called

  def test_cli_auth(self, *args):
    url = 'jelly://bean'
    token = 'cookies'

    api = Mock()
    api.getAuthURL.return_value = url
    api.getToken.return_value = token

    rtm.createRTM.return_value = api

    # Don't print during the tests
    CLIAuth.message = Mock()

    api = CLIAuth('K', 'S').auth()

    rtm.createRTM.assert_has_calls([
      call('K', 'S', 'dear_astrid'),
      # no test.login()
      call().getAuthURL(),
      call().getToken(),
      call('K', 'S', token),
      call().test.login(),
    ])

    webbrowser.open.called_once_with(url, True, True)

    # Url printed to screen.
    assert CLIAuth.message.call_args[0][2] == url

    assert INPUT_MOCK.call_count == 1
    assert INPUT_MOCK.call_args[0][0].startswith('Press Enter')

    # We should catch RTMAPIError and throw AuthError.
    CLIAuth.get_token_from_api = Mock()
    CLIAuth.api = Mock(side_effect=RTMAPIError('oops'))
    assert_raises(AuthError, CLIAuth(1, 2).auth)

  def test_importer_default_auth(self, *args):
    assert_equal(Importer().auth, CLIAuth)
