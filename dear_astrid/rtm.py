"""
Convert Astrid tasks to RTM tasks.
"""

__docformat__ = 'reStructuredText'

__all__ = [
  'format_date',
  'format_estimate',
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


