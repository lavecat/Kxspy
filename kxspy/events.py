from .objects import BaseObject
from dataclasses import dataclass

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