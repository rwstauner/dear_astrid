"""
Convert Astrid tasks to RTM tasks.
"""

__docformat__ = 'reStructuredText'

__all__ = [
  'format_date',
  'format_estimate',
  'format_priority',
]


def format_date(dto):
  """Format datetime unambiguously (isoformat).

  ::

    >>> import datetime
    >>> format_date(datetime.datetime(2012, 12, 25, 13))
    '2012-12-25T13:00:00'

  """
  return dto.isoformat() if dto else None


def format_estimate(seconds):
  """Convert estimated seconds to estimated minutes.

  ::

    >>> format_estimate(3600)
    '60 min'

  """

  # Preserve fractions but only show them if non-zero.
  minutes = seconds / 60.0
  if minutes.is_integer():
    minutes = int(minutes)

  # TODO: "="
  return '{} min'.format(minutes)


def format_priority(priority_):
  """Convert astrid importance to rtm priority.

  Astrid uses 0 for most important and 3 for none.
  RTM uses 1 for highest priority and 4 for none.

  ::

    >>> format_priority(0)
    1
    >>> format_priority(3)
    4

  """

  # If not in the valid range set to no priority.
  if not priority_ in range(0, 3):
    priority_ = 3

  # off by one error ;-)
  # TODO: "!"
  return int(priority_) + 1
