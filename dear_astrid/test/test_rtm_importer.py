# pylint: disable=wildcard-import,unused-wildcard-import,missing-docstring
# pylint: disable=no-member,maybe-no-member

from __future__ import absolute_import

from unittest import TestCase

from nose.tools import *
from mock import *

from dear_astrid.rtm.importer import *
from dear_astrid.test.helpers import *

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

  @patch('time.time', return_value=1373131732.100497)
  def test_importer_preparation(self, *args):
    # Skip auth logic since it's tested elsewhere

    api  = Mock()
    auth = Mock()
    auth.return_value.auth.return_value = api

    api.timelines.create.return_value.timeline = "5 o'clock"
    api.lists.add.return_value.list.id = 'tuttle'

    taskseries = Mock()
    taskseries.id = 'toothbrush'
    taskseries.task.id = 'boom!'
    api.tasks.add.return_value.list.taskseries = taskseries

    imp = Importer(auth=auth)
    imp.import_tasks([{'name':"That's a double!"}])

    list_name = 'Dear Astrid 1373131732.100497'

    # The rtm getter should be called twice (which means two sleeps).
    time.sleep.assert_has_calls([call(1), call(1)])

    imp._rtm.assert_has_calls([
      # The attributes called on the final object won't show up in this list
      # (unless we use PropertyMock) but later we test that the value was
      # received and passed correctly to other methods.

      # import_tasks()
      call.timelines.create(), # .timeline
      call.lists.add(timeline="5 o'clock", name=list_name), # .list.id

      # add_task()
      call.tasks.add(timeline="5 o'clock", list_id='tuttle',
        name="That's a double!", parse=0),
    ])

  def assert_add_task_api_calls(self, task, calls, raises=None, no_add=False):
    args = dict(
      timeline      = '3 days in tokyo',
      list_id       = '4077',
      taskseries_id = 'sniper',
      task_id       = 'kp',
    )

    imp = Importer()
    imp._rtm = Mock()
    imp.timeline = args['timeline']
    imp.list_id  = args['list_id']

    taskseries = Mock()
    taskseries.id      = args['taskseries_id']
    taskseries.task.id = args['task_id']
    imp._rtm.tasks.add.return_value.list.taskseries = taskseries

    if raises is not None:
      assert_raises(raises, lambda: imp.add_task(task))
    else:
      imp.add_task(task)

    # Append the args that are always required.
    for c in calls:
      c[-1].update(args)

    if not no_add:
      calls.insert(0, call.tasks.add(timeline=args['timeline'],
        list_id=args['list_id'], name=task['name'], parse=0))

    imp._rtm.assert_has_calls(calls)

  def test_no_task_name(self, *args):
    self.assert_add_task_api_calls(task={}, calls=[],
      raises=KeyError, no_add=True)

  def test_add_tasks(self, *args):
    self.assert_add_task_api_calls(
      task={
        'name':         u('squid'),
        'priority':     3,
        'due_date':     '2014-05-10T12:00:00Z',
        'repeat':       None,
        'completed':    False,
        'deleted':      False,
        'estimated':    None,
        'tags':         ['astrid'],
        'notes':        None,
      },
      calls=[
        call.tasks.addTags(tags='astrid'),
        call.tasks.setDueDate(due='2014-05-10T12:00:00Z',
          has_due_time=1, parse=0),
        call.tasks.setPriority(priority=3),
      ],
    )

    self.assert_add_task_api_calls(
      task={
        'name':         u('repeat and remind'),
        'priority':     3,
        'due_date':     '2013-06-04T18:55:01Z',
        'repeat':       'Every 12 days until 2014-07-19T17:55:01Z',
        'completed':    False,
        'deleted':      False,
        'estimated':    None,
        'notes':        u("First note\nHere"),
        'tags':         ['astrid', u('section 8'), u('Hard cheese'), 'astrid-notes'],
        'smart_add':    'should be ignored',
      },
      calls=[
        call.tasks.addTags(tags='astrid,section 8,Hard cheese,astrid-notes'),
        call.tasks.setDueDate(due='2013-06-04T18:55:01Z',
          has_due_time=1, parse=0),
        call.tasks.setPriority(priority=3),
        call.tasks.setRecurrence(
          repeat='Every 12 days until 2014-07-19T17:55:01Z'),
        call.tasks.notes.add(note_title=u("First note\nHere"),
          note_text=u("First note\nHere")),
      ],
    )

    self.assert_add_task_api_calls(
      task={
        'name':         u('Completed no priority'),
        'priority':     4,
        'completed':    True,
        'deleted':      False,
        'tags':         ['astrid', 'astrid-completed'],
      },
      calls=[
        call.tasks.addTags(tags='astrid,astrid-completed'),
        call.tasks.setPriority(priority=4),
        call.tasks.complete(),
      ],
    )

    self.assert_add_task_api_calls(
      task={
        'name':         u('Really important'),
        'priority':     1,
        'due_date':     None,
        'repeat':       None,
        'completed':    False,
        'deleted':      False,
        'estimated':    None,
        'notes':        u('No, really'),
        'tags':         ['astrid', u('section 8'), 'nifty', 'astrid-notes'],
      },
      calls=[
        call.tasks.addTags(tags='astrid,section 8,nifty,astrid-notes'),
        call.tasks.setPriority(priority=1),
        call.tasks.notes.add(note_title=u('No, really'),
          note_text=u('No, really')),
      ],
    )

    self.assert_add_task_api_calls(
      task={
        'name':         u('Funky ch&rs !n ^title a =b'),
        'priority':     2,
        'due_date':     None,
        'repeat':       'Every 3 weeks on Thursday',
        'completed':    False,
        'deleted':      False,
        'estimated':    '135 min',
        'notes':        None,
        'tags':         ['astrid', 'Hard cheese'],
      },
      calls=[
        call.tasks.addTags(tags='astrid,Hard cheese'),
        call.tasks.setEstimate(estimate='135 min'),
        call.tasks.setPriority(priority=2),
        call.tasks.setRecurrence(repeat='Every 3 weeks on Thursday'),
      ],
    )

    self.assert_add_task_api_calls(
      task={
        'name':         u('Completed and deleted'),
        'priority':     3,
        'due_date':     None,
        'repeat':       None,
        'completed':    True,
        'deleted':      True,
        'estimated':    '115 min',
        'notes':        'Enough said',
        'tags':         ['astrid', 'astrid-completed', 'astrid-deleted', 'astrid-notes'],
      },
      calls=[
        call.tasks.addTags(tags='astrid,astrid-completed,astrid-deleted,astrid-notes'),
        call.tasks.setEstimate(estimate='115 min'),
        call.tasks.setPriority(priority=3),
        call.tasks.notes.add(note_title='Enough said',
          note_text='Enough said'),
        call.tasks.complete(),
        call.tasks.delete(),
      ],
    )

    self.assert_add_task_api_calls(
      task={
        'name':         'empty list of notes',
        'notes':        [],
      },
      calls=[
      ],
    )

    self.assert_add_task_api_calls(
      task={
        'name':         'multiple notes',
        'notes':        ['text', 'stuff'],
      },
      calls=[
        call.tasks.notes.add(note_title='text', note_text='text'),
        call.tasks.notes.add(note_title='stuff', note_text='stuff'),
      ],
    )
