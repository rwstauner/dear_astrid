"""
Convert Astrid tasks to RTM tasks.
"""

__docformat__ = 'reStructuredText'

__all__ = [
  'format_date',
]


def format_date(dto):
  """Format datetime unambiguously (isoformat).

  ::

    >>> import datetime
    >>> format_date(datetime.datetime(2012, 12, 25, 13))
    '2012-12-25T13:00:00'

  """
  return dto.isoformat() if dto else None

