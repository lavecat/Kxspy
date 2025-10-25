from .objects import BaseObject , Stuff
from dataclasses import dataclass , field
from typing import Any

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
class ExchangeOnlineEvent(Event):
    """
    Event on exchange key online.
    """
    username: str
    v: str

@dataclass
class ExchangeOfflineEvent(Event):
    """
    Event on exchange key offline.
    """
    username: str

@dataclass
class ExchangeGameAliveEvent(Event):
    """
    Event on exchange key Game Alive.
    """
    alive: int

@dataclass
class ExchangeGameEnd(Event):
    """
    Event on exchange key Game End.
    """
    username: str
    kills: int
    damageDealt: int
    damageTaken: int
    duration: str
    position: str
    isWin: bool
    stuff: Stuff

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
    """
    Event on ConfirmGameStart.
    """
    ok: bool
    usernameChanged: bool

@dataclass
class GameStart(BaseObject):
    """
    Event on GameStart.
    """
    ok: bool
    system: bool
    players: list

@dataclass
class GameEnd(BaseObject):
    """
    Event on GameEnd.
    """
    left: str

@dataclass
class ConfirmGameEnd(BaseObject):
    """
    Event on GameEnd.
    """
    ok: bool

@dataclass
class KillEvent(BaseObject):
    """
    Event on KillEvent.
    """
    killer: str
    killed: str
    timestamp: int

@dataclass
class VersionUpdate(BaseObject):
    """
    Event on VersionUpdate.
    """
    v: str

@dataclass
class ChatMessage(BaseObject):
    """
    Event on ChatMessage.
    """
    user: str
    text: str
    timestamp: int
    system: bool

@dataclass
class VoiceData(BaseObject):
    """
    Event on VoiceData.
    """
    d: list
    u: str

@dataclass
class VoiceChatUpdate(BaseObject):
    """
    Event on VoiceChatUpdate.
    """
    user: str
    isVoiceChat: bool

@dataclass
class ConfirmVoiceChatUpdate(BaseObject):
    """
    Event on ConfirmVoiceChatUpdate.
    """
    ok: bool