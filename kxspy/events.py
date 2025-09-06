from .objects import BaseObject
from dataclasses import dataclass , field
from typing import List, Optional

class Event(BaseObject):
    """
    The class is a base event for websocket.
    """

@dataclass
class IdentifyEvent(Event):
    """
    IdentifyEvent. call when the websocket is ready.
    """
    uuid: str

@dataclass
class ExchangejoinEvent(Event):
    """
    Event on exchange join.
    """
    gameId: str
    exchangeKey: str

@dataclass
class BroadCasteEvent(Event):
    """
    Event on broadcaste.
    """
    msg: str

@dataclass
class HelloEvent(Event):
    """
    Event on hello.
    """
    heartbeat_interval: int

@dataclass
class HeartBeatEvent(Event):
    """
    Event on heartbeat.
    """
    ok: bool
    count: int
    players: list

@dataclass
class ConfirmGameStart(BaseObject):
    ok: bool
    usernameChanged: bool

@dataclass
class GameStart(BaseObject):
    ok: bool
    system: bool
    players: list

@dataclass
class GameEnd(BaseObject):
    ok: bool
    system: bool
    players: list