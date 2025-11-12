"""
kxspy
---------
:copyright: (c) 2025 lavecat
:license: MIT, see LICENSE for more details.
"""

__title__ = 'kxspy'
__author__ = 'lavecat'
__license__ = 'MIT'
__copyright__ = 'Copyright 2025-present lavecat'
__version__ = '1.0.4b'

from .client import Client
from .objects import *
from .events import *
from .rest import RestApi
from typing import Type, Callable



# https://github.com/devoxin/Lavalink.py/blob/development/lavalink/__init__.py#L28-L60
def listener(*events: Type[Event]):
    """
    Marks this function as an event listener for Kxspy.

    Example:
        @listener()
        async def on_any_event(self, event): ...

        @listener(ExchangeGameEnd)
        async def on_game_end(self, event: ExchangeGameEnd): ...
    """
    def wrapper(func: Callable):
        setattr(func, "_kxspy_events", events)
        return func
    return wrapper