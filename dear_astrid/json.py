"""Dump task list as JSON."""

from __future__ import absolute_import

from datetime import datetime

try:
  import simplejson as json
except ImportError:
  import json

def encode_complex(obj):
  """Customize json encoding for complex objects."""

  if isinstance(obj, datetime):
    return encode_datetime(obj)

  raise TypeError(repr(obj) + " is not JSON serializable")

def encode_datetime(obj):
  """Represent datetime in JSON with standard ISO-8601 format."""
  # Use isoformat() to get possible fractional seconds.
  # The datetime objects should be in UTC (so isoformat will append '+00:00').
  return obj.isoformat()

def dumps(struct, **kwargs):
  """Dump task list as JSON string."""
  return json.dumps(struct, default=encode_complex, **kwargs)

def loads(string, **kwargs):
  """Load object from JSON string."""
  return json.loads(string, **kwargs)
