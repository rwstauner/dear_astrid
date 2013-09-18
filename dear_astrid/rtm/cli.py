"""
CLI (Command Line Interface) classes for RTM Importer.
"""

from __future__ import absolute_import, print_function

__docformat__ = 'reStructuredText'

import webbrowser

from dear_astrid.rtm.importer import *


# TODO: Is there a better way to share class methods than multiple inheritance?
class CLIHelpers(object):
  def prompt(self, text):
    try:
      answer = raw_input(text)
    except NameError:
      answer = input(text)
    return answer

  def message(self, *args):
    for arg in args:
      print(arg)


class CLIAuth(BaseAuth, CLIHelpers):
  def __init__(self, key, secret, cache=None):
    BaseAuth.__init__(self, key, secret)
    # TODO: self.cache = cache if cache else os.path.expanduser()

  # TODO: store auth token (~/.dear_astrid ?) for repeats
  def get_token_from_file(self):
    return False

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
