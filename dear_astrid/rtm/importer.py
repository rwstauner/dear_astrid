"""
Import rtm-formatted tasks through the RTM API.

This product uses the Remember The Milk API
but is not endorsed or certified by Remember The Milk.
"""

from __future__ import absolute_import

__docformat__ = 'reStructuredText'

import sys
if sys.version_info <= (3,):
  import string
import time
import webbrowser

import rtm

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
    self.tr = self.maketrans('89abcdef01234567', '0123456789abcdef')

  # 2to3
  maketrans = string.maketrans if sys.version_info <= (3,) else str.maketrans

  def __get__(self, obj, cls):
    return getattr(obj, self.attr).translate(self.tr)
  def __set__(self, obj, val):
    setattr(obj, self.attr, val)

class Importer(object):
  def __init__(self):
    self._rtm  = None
    self.timeline = None
    self.list_id  = None

    # Please obtain your own api key/secret (it's easy!) rather than using
    # these in another app: https://www.rememberthemilk.com/services/api/
    self.key    = '7c564da6c23abeda8e028bf2390971c0'
    self.secret = 'a885323e4a010a8d'

  @_slow
  def rtm(self):
    return self._rtm

  def import_tasks(self, tasks):
    self.timeline = self.rtm.timelines.create().timeline
    self.list_id  = self.rtm.lists.add(timeline=self.timeline,
      name='Dear Astrid ' + time.time()).list.id

    for task in tasks:
      self.add_task(task)

  def add_task(self, task):
    # The pyrtm module is dynamic.
    # pylint: disable=no-member

    added = self.rtm.tasks.add(timeline=self.timeline,
      name=task['name'], parse=0)

    args = dict(
      timeline      = self.timeline,
      list_id       = self.list_id,
      taskseries_id = added.list.taskseries.id,
      task_id       = added.list.taskseries.task.id,
    )

    # Should this be setTags?
    rtm.tasks.addTags(tags=','.join(task['tags']), **args)

    if task['due_date']:
      # TODO: Can we determine has_due_time?
      rtm.tasks.setDueDate(due=task['due_date'], has_due_time=1, parse=0, **args)

    if task['estimated']:
      rtm.tasks.setEstmate(estimate=task['estimate'], **args)

    if task['priority']:
      rtm.tasks.setPriority(priority=task['priority'], **args)

    if task['repeat']:
      rtm.tasks.setRecurrence(repeat=task['repeat'], **args)

    if task['notes']:
      for note in task['notes']:
        rtm.tasks.notes.add(note_title=note, note_text=note, **args)

    # TODO: does Astrid do URLs? rtm.setURL(url=task['url'], **args)

    # do the status changes last
    if task['completed']:
      rtm.tasks.complete(**args)

    if task['deleted']:
      rtm.tasks.delete(**args)

    return added

  key    = _rot('key')
  secret = _rot('secret')

RTMAPIError = rtm.rtm.RTMAPIError
class AuthError(RTMAPIError):
  pass

class BaseAuth(object):
  def __init__(self, key, secret, token=None):
    self.key    = key
    self.secret = secret
    self.token  = token

  def api(self, token=None, test_login=True):
    # pylint: disable=no-member
    if token is None:
      token = self.token
    api = rtm.createRTM(self.key, self.secret, token)
    if test_login:
      api.test.login()
    return api

  def auth(self):
    return self.api(self.token)

class CLIAuth(BaseAuth):
  def prompt(self, text):
    try:
      answer = raw_input(text)
    except NameError:
      answer = input(text)
    return answer

  def message(self, *args):
    for arg in args:
      print(arg)

  def get_token_from_api(self):
    # Instantiate api with fake token to get url.
    api = self.api('dear_astrid', test_login=False)
    url = api.getAuthURL()

    webbrowser.open(url, True, True)
    self.message(
      "You must authorize this app with RTM.",
      "If a browser does not open visit this URL:",
      url,
    )
    self.prompt('Press Enter after you have authorized this app through RTM.')

    return api.getToken()

  def auth(self):
    token = self.get_token_from_api()
    try:
      return self.api(token)
    except RTMAPIError:
      raise AuthError("Failed to authorize app with RTM.")
