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

@patch('time.sleep')
@patch('rtm.createRTM')
@patch(INPUT_FUNC, new=INPUT_MOCK)
class TestCLIImporter(TestCase):

  def setUp(self):
    self.imp = CLIImporter()
    self.imp.message = Mock()
    self.imp.prompt  = Mock()
    self.imp._rtm    = Mock()

  def test_default_auth(self, *args):
    assert_true(self.imp.auth, CLIAuth)

  def test_display_task_smart_add(self, *args):
    self.imp.display_task({'smart_add': 'smarty pants'})
    self.imp.message.called_once_with('smarty pants')

  def test_display_task_name(self, *args):
    self.imp.display_task({'name': 'namey pants'})
    self.imp.message.called_once_with('namey pants')

  def test_display_task_format(self, *args):
    self.imp.display_task({'name': 'namey pants'}, format=' <={0}=> ')
    self.imp.message.called_once_with(' <=namey pants=> ')

  def test_rtm_progress_indicator(self, *args):
    self.imp.rtm.remember()
    self.imp.rtm.the('milk')
    self.imp.rtm.bob.t.monkey()

    # Print a dot for each api call.
    self.imp.message.assert_has_calls([
      call('.', end=''),
      call('.', end=''),
      call('.', end=''),
    ])

    # Sanity check (what we just called is all that has been called.
    self.imp._rtm.assert_has_calls([
      call.remember(),
      call.the('milk'),
      call.bob.t.monkey(),
    ])

    # Ensure parent method is used and sleep is performed for each call.
    time.sleep.assert_has_calls([call(1), call(1), call(1)])


  def capture_import_tasks(self, tasks, prompt=None):
    self.imp.prompt.return_value = prompt
    # Mock the superclass method to test if it gets called.
    with patch('dear_astrid.rtm.cli.Importer.import_tasks') as patched:
      self.imp.import_tasks(tasks)
      return patched


  def test_import_tasks_cancel(self, *args):
    self.capture_import_tasks([{'hi': 'there'}], prompt=':-P') \
      .assert_has_calls([])

    self.imp.message.assert_has_calls([ call(' (unknown)') ])

  def test_import_tasks_confirm(self, *args):
    self.capture_import_tasks([{'name': '50'}], prompt='y') \
      .assert_has_calls([call([{'name': '50'}])])

    self.imp.message.assert_has_calls([ call(' 50') ])

  def test_import_tasks(self, *args):
    tasks = [
      {'name': 'mine field'},
      {'smart_add': 'downtown berlin #go', 'name': 'berlin', 'tags': ['go']},
    ]
    self.imp.import_tasks(tasks)

    self.imp.message.assert_has_calls([
      # Confirm tasks.
      call(' mine field'),
      call(' downtown berlin #go'),
      # Show initial api calls.
      call('.', end=''),
      call('.', end=''),
      # Add tasks.
      call('Adding: mine field', end=''),
      call('.', end=''),
      call(''),
      call('Adding: downtown berlin #go', end=''),
      call('.', end=''),
      call('.', end=''), # tags
      call(''),
    ])

  def test_add_task(self, *args):
    with patch('dear_astrid.rtm.cli.Importer.add_task') as add_task_patch:
      self.imp.add_task({'name': 'mail a bear'})
      self.imp.message.assert_has_calls([
        call('Adding: mail a bear', end=''),
        call(''),
      ])
      # Assert dispatch to parent method.
      add_task_patch.assert_has_calls([
        call({'name': 'mail a bear'}),
      ])

  def test_add_task_progress_indicator(self, *args):
    self.imp.add_task({
      'smart_add': 'read how to',
      'name':      'mail a bear',
      'tags':      ['astrid', 'mechanics'],
      'notes':     ['bored', 'bored bored'], # 2 calls
      'priority':  1,
    })

    time.sleep.assert_has_calls(
      [call(1) for i in range(5)]
    )
    self.imp.message.assert_has_calls(
      [call('Adding: read how to', end='')] +
      [call('.', end='') for i in range(5)] +
      [call('')]
    )
