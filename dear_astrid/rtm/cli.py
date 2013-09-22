"""
CLI (Command Line Interface) classes for RTM Importer.
"""

from __future__ import absolute_import, print_function

__docformat__ = 'reStructuredText'

import webbrowser

from dear_astrid.rtm.importer import *


# TODO: Is there a better way to share class methods than multiple inheritance?
class CLIHelpers(object):
  """Add helper methods for cli input/output to classes."""
  # pylint: disable=no-self-use
  def prompt(self, text):
    """Prompt the user for a value."""
    try:
      # py2
      answer = raw_input(text)
    except NameError:
      # pylint: disable=bad-builtin
      # py3k
      answer = input(text)
    return answer

  def message(self, *args, **kwargs):
    """Print each argument to STDOUT."""
    for arg in args:
      print(arg, **kwargs)


class CLIAuth(BaseAuth, CLIHelpers):
  """Authorize RTM importer using the command line as an interface."""

  def __init__(self, key, secret, cache=None):
    BaseAuth.__init__(self, key, secret)
    # TODO: self.cache = cache if cache else os.path.expanduser()

  # TODO: store auth token (~/.dear_astrid ?) for repeats
  def get_token_from_file(self):
    return False

  def get_token_from_api(self):
    """Get token from API by opening a web browser."""

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
    token = self.get_token_from_file()
    if token:
      # Make sure token is still authorized.
      try:
        return self.api(token)
      except RTMAPIError:
        self.message("Previous token is no longer valid.")

    token = self.get_token_from_api()
    try:
      return self.api(token)
    except RTMAPIError:
      raise AuthError("Failed to authorize app with RTM.")


class CLIImporter(Importer, CLIHelpers):

  """Import astrid backup xml into RTM on the command line."""

  def __init__(self, auth=CLIAuth):
    super(CLIImporter, self).__init__(auth=auth)

  def display_task(self, task, spec='{0}', **kwargs):
    """Print description of task using SmartAdd property or task name."""
    self.message(
      spec.format(task.get('smart_add', task.get('name', '(unknown)'))),
      **kwargs
    )

  def import_tasks(self, tasks):
    """Confirm task list before importing."""

    for task in tasks:
      self.display_task(task, spec=' {0}')

    cont = self.prompt('Import tasks? (y/n):')
    if not cont.lower().startswith('y'):
      return

    super(CLIImporter, self).import_tasks(tasks)

  def add_task(self, task):
    """Print description of task before adding and show progress indicator."""

    self.display_task(task, spec='Adding: {0}', end='')

    super(CLIImporter, self).add_task(task)

    # Append newline.
    self.message('')

  @property
  def rtm(self):
    # self.before_rtm ?
    self.message('.', end='')
    return super(CLIImporter, self).rtm
