import logging
import typing as t
from .ws import WS
from .events import Event
from .utils import get_random_username
from .rest import RestApi

_LOG = logging.getLogger("kxspy.client")

class Client:
    """
    The main class.
    """
    def __init__(
        self,
        ws_url: str = "wss://network.kxs.rip/",
        rest_url: str = "https://network.kxs.rip",
        username: str = get_random_username(),
        enablevoicechat: bool = False,
        exchangekey: str = None,
        admin_key: str = None,
        connect: bool = True,
    ) -> None:
        self.ws = WS(
            ws_url=ws_url,
            username=username,
            enable_voice_chat=enablevoicechat,
            exchange_key=exchangekey,
            connect=connect
        )
        self.username = username
        self.rest = RestApi(rest_url,admin_key)
        self.emitter = self.ws.emitter
        self._registered_listeners: t.List[t.Tuple[t.Any, t.Callable, t.Type[Event]]] = []


    def add_event_hooks(self, obj):
        """
        Scans the provided class ``obj`` for functions decorated with :func:`listener`,
        and sets them up to process Lavalink events.
        """
        for attr_name in dir(obj):
            method = getattr(obj, attr_name)
            events = getattr(method, "_kxspy_events", None)
            if not events:
                continue

            if not events:
                self.emitter.add_listener(event=None, func=method)
            else:
                for ev in events:
                    self.emitter.add_listener(event=ev, func=method)

    def remove_event_hooks(self, obj: t.Any):
        """
        Removes all previously registered listeners for an object.
        """
        to_remove = [r for r in self._registered_listeners if r[0] == obj]
        for _, method, ev in to_remove:
            try:
                self.emitter.remove_listener(event=ev, func=method)
                _LOG.debug(f"Removed listener: {method.__name__} for {ev}")
            except Exception as e:
                _LOG.warning(f"Failed to remove listener {method.__name__}: {e}")

            self._registered_listeners.remove((_, method, ev))

    async def connect(self):
        """Connect to Kxs Network."""
        await self.ws.connect()

    async def join_game(self, gameId):
        """Join a game by its ID."""
        await self.ws.send({"op": 3, "d": {"gameId": gameId,"user": self.username}})

    async def leave_game(self):
        """Leave the current game."""
        await self.ws.send({"op": 4, "d": {}})

    async def report_kill(self,killer: str, killed: str):
        """Report a kill in the game"""
        await self.ws.send({"op": 5, "d": {"killer":killer,"killed":killed}})

    async def check_version(self):
        """Report a kill in the game"""
        await self.ws.send({"op": 6, "d": {}})

    async def send_message(self,text: str):
        """Report a kill in the game"""
        await self.ws.send({"op": 7, "d": {"text":text}})

    async def update_voicechat(self,isVoiceChat: bool):
        """Report a kill in the game"""
        await self.ws.send({"op": 98, "d": {"isVoiceChat":isVoiceChat}})



