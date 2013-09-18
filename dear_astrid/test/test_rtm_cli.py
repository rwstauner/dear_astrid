# pylint: disable=wildcard-import,unused-wildcard-import,missing-docstring
# pylint: disable=no-member,maybe-no-member

from __future__ import absolute_import

from unittest import TestCase

from nose.tools import *
from mock import *
import rtm
import webbrowser

from dear_astrid.rtm.cli      import *


try:
  raw_input
  INPUT_FUNC = '__builtin__.raw_input'
except NameError:
  INPUT_FUNC = 'builtins.input'
INPUT_MOCK = MagicMock()


@patch('rtm.createRTM')
@patch('webbrowser.open')
@patch(INPUT_FUNC, new=INPUT_MOCK)
class TestRTMCLI(TestCase):
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
    assert_equal(CLIAuth.message.call_args[0][2], url)

    assert_equal(INPUT_MOCK.call_count, 1)
    assert_true(INPUT_MOCK.call_args[0][0].startswith('Press Enter'))

    # We should catch RTMAPIError and throw AuthError.
    CLIAuth.get_token_from_api = Mock()
    CLIAuth.api = Mock(side_effect=RTMAPIError('oops'))
    assert_raises(AuthError, CLIAuth(1, 2).auth)
