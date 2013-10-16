"""
Convert Astrid tasks to Remember The Milk.
"""

from __future__ import absolute_import, unicode_literals

# pylint: disable=wildcard-import

from dear_astrid.rtm.format import *
from dear_astrid.rtm.format import __all__ as _format_all

from dear_astrid.rtm.importer import *
from dear_astrid.rtm.importer import __all__ as _importer_all

from dear_astrid.rtm.cli import *
from dear_astrid.rtm.cli import __all__ as _cli_all


# With unicode_literals on everywhere I seem to get this error on py2:
#   TypeError: Item in ``from list'' not a string
__all__ = [str(s) for s in _format_all + _importer_all + _cli_all]
