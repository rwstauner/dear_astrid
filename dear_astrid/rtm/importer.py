"""
Import rtm-formatted tasks through the RTM API.

This product uses the Remember The Milk API
but is not endorsed or certified by Remember The Milk.
"""

from __future__ import absolute_import, unicode_literals

__docformat__ = 'reStructuredText'

import os
import sys
PY3K = sys.version_info >= (3,)
if not PY3K:
  import string
import time

import rtm

__all__ = [
  'Importer',
  'BaseAuth',
  'AuthError',
  'RTMAPIError',
]

class _slow(object):
  def __init__(self, fget):
    self.fget  = fget

  # RTM docs request limiting API calls to one per second.
  def __get__(self, obj, cls):
    time.sleep(1)
    return self.fget(obj)

class _rot(object):
  def __init__(self, fname):
    self.fname = fname
    self.attr  = ' ' + fname
    # Cast unicode_literal to str for 3to2.
    self.tr = self.maketrans(str('89abcdef01234567'), str('0123456789abcdef'))

  if not PY3K:
    def maketrans(self, from_, to_):
      return string.maketrans(from_, to_)
  else:
    def maketrans(self, from_, to_):
      return str.maketrans(from_, to_)

  def __get__(self, obj, cls):
    return getattr(obj, self.attr).translate(self.tr)

  def __set__(self, obj, val):
    # Cast unicode_literal to str for 3to2.
    setattr(obj, self.attr, str(val))


RTMAPIError = rtm.rtm.RTMAPIError
class AuthError(RTMAPIError):
  """Represent failure to authenticate as subclass of RTMAPIError."""
  pass


class BaseAuth(object):
  """Base class for Authorization.  Gets values from ENV."""

  def __init__(self, key=None, secret=None, token=None):
    self.key    = key    or self.get('key')
    self.secret = secret or self.get('secret')
    self.token  = token  or self.get('token')

  def get(self, var):
    """Get auth value from env."""
    # pylint: disable=no-self-use
    return os.getenv('ASTRID_RTM_{0}'.format(var.upper()))

  def api(self, token=None, test_login=True):
    """Create RTM api client and test login."""
    # pylint: disable=no-member
    if token is None:
      token = self.token

    api = rtm.createRTM(self.key, self.secret, token)

    if test_login:
      api.test.login()

    return api

  def auth(self):
    """Authorize against RTM return client object."""
    return self.api(self.token)


class Importer(object):
  """Import tasks into RTM."""

  default_auth = BaseAuth

  def __init__(self, auth=None):
    #self.transactions = []
    self._rtm  = None
    self.timeline = None
    self.list_id  = None
    if auth is not None:
      self.auth = auth
    else:
      self.auth = self.default_auth

    # Please obtain your own api key/secret (it's easy!) rather than using
    # these in another app: https://www.rememberthemilk.com/services/api/
    self.key    = '7c564da6c23abeda8e028bf2390971c0'
    self.secret = 'a885323e4a010a8d'

  @_slow
  def rtm(self):
    """RTM API client (proprty)"""
    if not self._rtm:
      self._rtm = self.auth(self.key, self.secret).auth()
    return self._rtm

  def import_tasks(self, tasks):
    """Create new list and add tasks to it."""

    self.timeline = self.rtm.timelines.create().timeline

    # TODO: make list name customizable?
    list_name = 'Dear Astrid {0:f}'.format(time.time())

    self.list_id  = self.rtm.lists.add(timeline=self.timeline,
      name=list_name).list.id

    for task in tasks:
      self.add_task(task)

  def add_task(self, task):
    """Call RTM api to add task and set it's preoperties."""

    # The pyrtm module is dynamic.
    # pylint: disable=no-member

    added = self.rtm.tasks.add(timeline=self.timeline,
      name=task['name'], list_id=self.list_id, parse=0)

    # TODO: record undoable transactions and undo them upon kb interrupt
    #if added.transaction.undoable == "1":
      #self.transactions.append(added.transaction.id)

    args = dict(
      timeline      = self.timeline,
      list_id       = self.list_id,
      taskseries_id = added.list.taskseries.id,
      task_id       = added.list.taskseries.task.id,
    )

    if task.get('tags', None):
      # Should this be setTags?
      self.rtm.tasks.addTags(tags=','.join(task['tags']), **args)

    if task.get('due_date', None):
      self.rtm.tasks.setDueDate(due=task['due_date'],
        # TODO: Can we determine has_due_time?
        has_due_time=1,
        # We're using iso8601 so we don't need them to be specially parsed.
        parse=0,
        **args)

    if task.get('estimated', None):
      self.rtm.tasks.setEstimate(estimate=task['estimated'], **args)

    if task.get('priority', None):
      self.rtm.tasks.setPriority(priority=task['priority'], **args)

    if task.get('repeat', None):
      self.rtm.tasks.setRecurrence(repeat=task['repeat'], **args)

    if task.get('notes', None):
      if isinstance(task['notes'], list):
        notes = task['notes']
      else:
        notes = [ task['notes'] ]
      for note in notes:
        self.rtm.tasks.notes.add(note_title=note, note_text=note, **args)

    if task.get('url', None):
      self.rtm.tasks.setURL(url=task['url'], **args)

    # do the status changes last
    if task.get('completed', None):
      self.rtm.tasks.complete(**args)

    if task.get('deleted', None):
      self.rtm.tasks.delete(**args)

    return added

  key    = _rot('key')
  secret = _rot('secret')
