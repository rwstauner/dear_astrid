# pylint: disable=wildcard-import,unused-wildcard-import,missing-docstring
# pylint: disable=no-member,maybe-no-member

from __future__ import absolute_import

import os
import time
from unittest import TestCase

from nose.tools import *
from mock import *
import rtm

from dear_astrid.rtm.importer import *
from dear_astrid.test.helpers import *

@patch('time.sleep')
@patch('rtm.createRTM')
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

  def test_importer_default_auth(self, *args):
    assert_equal(Importer().auth, BaseAuth)

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
        'name':         'squid',
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
        'name':         'repeat and remind',
        'priority':     3,
        'due_date':     '2013-06-04T18:55:01Z',
        'repeat':       'Every 12 days until 2014-07-19T17:55:01Z',
        'completed':    False,
        'deleted':      False,
        'estimated':    None,
        'notes':        "First note\nHere",
        'tags':         ['astrid', 'section 8', 'Hard cheese', 'astrid-notes'],
        'smart_add':    'should be ignored',
      },
      calls=[
        call.tasks.addTags(tags='astrid,section 8,Hard cheese,astrid-notes'),
        call.tasks.setDueDate(due='2013-06-04T18:55:01Z',
          has_due_time=1, parse=0),
        call.tasks.setPriority(priority=3),
        call.tasks.setRecurrence(
          repeat='Every 12 days until 2014-07-19T17:55:01Z'),
        call.tasks.notes.add(note_title="First note\nHere",
          note_text="First note\nHere"),
      ],
    )

    self.assert_add_task_api_calls(
      task={
        'name':         'Completed no priority',
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
        'name':         'Really important',
        'priority':     1,
        'due_date':     None,
        'repeat':       None,
        'completed':    False,
        'deleted':      False,
        'estimated':    None,
        'notes':        'No, really',
        'tags':         ['astrid', 'section 8', 'nifty', 'astrid-notes'],
      },
      calls=[
        call.tasks.addTags(tags='astrid,section 8,nifty,astrid-notes'),
        call.tasks.setPriority(priority=1),
        call.tasks.notes.add(note_title='No, really',
          note_text='No, really'),
      ],
    )

    self.assert_add_task_api_calls(
      task={
        'name':         'Funky ch&rs !n ^title a =b',
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
        'name':         'Completed and deleted',
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

@patch('rtm.createRTM')
class TestBaseAuth(TestCase):

  def setUp(self):
    self.env_vars = ['ASTRID_RTM_%s' % var.upper() for var in ('key', 'secret', 'token')]
    for var in self.env_vars:
      os.environ[var] = 'e %s' % var[11:13].lower()

  def tearDown(self):
    for var in self.env_vars:
      del os.environ[var]

  def test_args(self, *args):
    api = BaseAuth('k', 's', 't').auth()
    rtm.createRTM.assert_called_once_with('k', 's', 't')
    api.test.login.assert_called_once_with()

  def test_env(self, *args):
    api = BaseAuth().auth()
    rtm.createRTM.assert_called_once_with('e ke', 'e se', 'e to')
    api.test.login.assert_called_once_with()

  def test_both(self, *args):
    api = BaseAuth('k1').auth()
    rtm.createRTM.assert_called_once_with('k1', 'e se', 'e to')
    api.test.login.assert_called_once_with()

class TestBaseAuthErrors(TestCase):

  def setUp(self):
    self.patches = [
      patch('rtm.createRTM'),
    ]
    for patcher in self.patches:
      patcher.start()

    self.login = Mock()
    # Prepare to test Exceptions raised on login test.
    self.login.test.login.side_effect = AuthError('oops')
    rtm.createRTM.return_value = self.login

  def tearDown(self):
    for patcher in self.patches:
      patcher.stop()

  def test_auth(self, *args):
    auth = BaseAuth(1, 2, 3)
    assert_raises(AuthError, auth.auth)
    rtm.createRTM.assert_called_once_with(1, 2, 3)
    self.login.assert_has_calls([call.test.login()])

  def test_api(self, *args):
    auth = BaseAuth(1, 2, 3)
    assert_raises(AuthError, auth.api)
    rtm.createRTM.assert_called_once_with(1, 2, 3)
    self.login.assert_has_calls([call.test.login()])

  def test_api_no_login(self, *args):
    auth = BaseAuth(1, 2, 3)
    try:
      auth.api(test_login=False)
    except AuthError:
      assert False
    else:
      assert True

    assert not self.login.called
